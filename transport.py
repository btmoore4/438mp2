from helper import *
from sender import *
from receiver import *

import sys
import socket
import random
import threading
import time


"""
Implements the MP2 socket class, as described below
"""

#Defined Errors
class MP2SocketError(Exception):
    """ Exception base class for protocol errors """
    pass
class SYN_Error(MP2SocketError):
    def __init__(self, message):
        self.message = message
class SYNACK_Error(MP2SocketError):
    def __init__(self, message):
        self.message = message
class ACK_Error(MP2SocketError):
    def __init__(self, message):
        self.message = message

class MP2Socket:
    def __init__(self):
        self.seq = random.randint(1, 1000)
	print self.seq
        sys.stderr.write(str(self.seq) + "\n")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = "INIT"
        self.buffer = ""
        self.timeout_mess = None
        self.addr = None
        self.type = None
        self.sock_type= None
        self.synACK = None

    def resend_mess(self):
        print "TIMEOUT - SENDING SYN AGAIN"
        self.sock.sendto(self.timeout_mess, self.addr)
        print threading.active_count()

    def connect(self, addr):
        """
        Connects to a remote MP2 transport server. Address is specified by a
        pair `(host,port)`, where `host` is a string with either an IP address
        or a hostname, and `port` is a UDP port where data will arrive

        A client must call `connect` as the first operation on the socket.

        This call raises MP2SocketError if a connection cannot be established.
        It does not return any value on success
        """
        # ----- SEND SYN -----
        print 'BEGINNING CONNECT'
        print 'SEND SYN'
        self.timeout_mess = synMess(self.seq)
        self.sock.sendto(self.timeout_mess, addr)
        sender_rtt = time.time()
        self.addr = addr
        self.timer = TCPTimeout(TIMEOUT, self.resend_mess)
        self.timer.start()

        # ----- WAITING FOR SYNACK -----
        print 'WAITING FOR SYNACK'
        raw_msg, server_addr = self.sock.recvfrom(PKT)
        self.timer.stop()
        sender_rtt = sender_rtt - time.time()
        synack_mess = decodeMess(raw_msg)
        #print synack_mess

        # ----- IF INCORRECT SYNACK -----
        if synack_mess[SYN] != 1 or synack_mess[ACK] != self.seq + 1:
            raise SYNACK_Error("Client expecting valid SYNACK message.")

        # ----- SEND ACK -----
        print 'SEND ACK'
        self.sock.sendto(ackMess(synack_mess[SEQ]), addr)

        # ----- CONNECTION -----
        print "CONNECTION ESTABLISHED"
        self.sock_type = "S"
        self.type = Sender(self.sock, self.seq, addr, sender_rtt)

    def accept(self, port):
        """
        Waits for a connection on a given (UDP) port. Returns a pair
        `(host,port)` representing the client address.

        A server must call `accept` as the first operation on the socket.

        Raises MP2SocketError if an error is encountered (e.g., UDP port
        already in use)
        """
        # ----- WAITING FOR SYN -----
        print 'BEGINNING ACCEPT'
        print 'WAITING FOR SYN'
        self.sock.bind(('', port))
        raw_msg, client_addr = self.sock.recvfrom(PKT)
        syn_mess = decodeMess(raw_msg)

        # ----- IF MESS IS NOT SYN -----
        if syn_mess[SYN] != 1:
            raise SYN_Error("Server expecting SYN message.")

        # ----- SEND SYN_ACK -----
        print 'SEND SYN_ACK' 
        self.timeout_mess = synackMess(self.seq, syn_mess[SEQ])
        self.addr = client_addr
        self.addr = client_addr
        self.sock.sendto(self.timeout_mess, client_addr)
        self.timer = TCPTimeout(TIMEOUT, self.resend_mess)
        self.timer.start()

        # ----- WAIT FOR ACK -----
        print 'WAIT FOR ACK'
        raw_msg, client_addr = self.sock.recvfrom(PKT)
        self.timer.stop()
        ack_mess = decodeMess(raw_msg)

        # ----- IF INCORRECT ACK -----
        if ack_mess[ACK] != self.seq + 1:
            #raise ACK_Error("Server expecting valid ACK message.")
            sys.stderr.write('stderr - CONNECTION ESTABLISHED with BAD ACK\n')
            self.sock_type = "R"
            self.type = Receiver(self.sock, self.seq, ack_mess, client_addr)
            return client_addr

        # ----- CONNECTION -----
        print "CONNECTION ESTABLISHED"
        sys.stderr.write('stderr - CONNECTION ESTABLISHED\n')
        self.sock_type = "R"
        self.type = Receiver(self.sock, self.seq, None, client_addr)
        return client_addr

    def send(self, data):
        """
        Send data to the remote destination. Data may be of arbitrary length
        and should be split into smaller packets. This call should block
        for flow control, though you can buffer some small amount of data.
        This call should behave like `sendall` in Python; i.e., all data must
        be sent. Does not return any value.

        Should be called on a socket after connect or accept
        """
        self.type.send(data)

    def recv(self, length):
        """
        Receive data from the remote destination. Should wait until data
        is available, then return up to `length` bytes. Should return "" when
        the remote end closes the socket
        """
 
        """
        while True:
            raw_msg, send_addr = self.sock.recvfrom(PKT+20)
            print raw_msg
            #data_msg = decodeMess(raw_msg)
            #ack_mess = ackDataMess(self.seq, data_msg[SEQ] + data_msg[LEN]) 
            #self.sock.sendto(ack_mess, send_addr)
        """
        return self.type.receiver_recv(length)

    def close(self):
        """
        Closes the socket and informs the other end that no more data will
        be sent
        """
        if self.sock_type == "R":
            self.type.receiver_stop()
        else:
            self.type.stop()


