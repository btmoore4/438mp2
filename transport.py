from helper import *
from sender import *

import socket
import random

"""
Implements the MP2 socket class, as described below
"""

SEQ = 0
ACK = 1
SYN = 2
FIN = 3
LEN = 4
DATA = 5

PKT = 2048
PKT2 = 4

class MP2Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = "INIT"
        self.seq = random.randint(1, 1000)
        self.sender = None

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
        print 'SEND SYN'
        self.sock.sendto(synMess(self.seq), addr)

        # ----- WAITING FOR SYNACK -----
        print 'WAITING FOR SYNACK'
        raw_msg, server_addr = self.sock.recvfrom(PKT)
        synack_mess = decodeMess(raw_msg)
        print synack_mess

        # ----- IF INCORRECT SYNACK -----
        if synack_mess[SYN] != 1 or synack_mess[ACK] != self.seq + 1:
            raise SYNACK_Error("Client expecting valid SYNACK message.")

        # ----- SEND ACK -----
        print 'SEND ACK'
        self.sock.sendto(ackMess(synack_mess[SEQ]), addr)

        # ----- CONNECTION -----
        print "CONNECTION ESTABLISHED"
        self.sender = Sender(self.sock, self.seq, addr)

    def accept(self, port):
        """
        Waits for a connection on a given (UDP) port. Returns a pair
        `(host,port)` representing the client address.

        A server must call `accept` as the first operation on the socket.

        Raises MP2SocketError if an error is encountered (e.g., UDP port
        already in use)
        """
        # ----- WAITING FOR SYN -----
        print 'WAITING FOR SYN'
        self.sock.bind(('', port))
        raw_msg, client_addr = self.sock.recvfrom(PKT)
        syn_mess = decodeMess(raw_msg)
        print syn_mess

        # ----- IF MESS IS NOT SYN -----
        if syn_mess[SYN] != 1:
            raise SYN_Error("Server expecting SYN message.")

        # ----- SEND SYN_ACK -----
        print 'SEND SYN_ACK' 
        self.sock.sendto(synackMess(self.seq, syn_mess[SEQ]), client_addr)

        # ----- WAIT FOR ACK -----
        print 'WAIT FOR ACK'
        raw_msg, client_addr = self.sock.recvfrom(PKT)
        ack_mess = decodeMess(raw_msg)
        print ack_mess

        # ----- IF INCORRECT ACK -----
        if ack_mess[ACK] != self.seq + 1:
            raise ACK_Error("Server expecting valid ACK message.")

        # ----- CONNECTION -----
        print "CONNECTION ESTABLISHED"
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
        self.sender.send(data)

    def recv(self, length):
        """
        Receive data from the remote destination. Should wait until data
        is available, then return up to `length` bytes. Should return "" when
        the remote end closes the socket
        """
        #Basic Receiver
        while True:
            raw_msg, send_addr = self.sock.recvfrom(PKT)
            data_msg = decodeMess(raw_msg)
            print data_msg
            ack_mess = ackDataMess(self.seq, data_msg[SEQ] + data_msg[LEN]) 
            self.sock.sendto(ack_mess, send_addr)

    def close(self):
        """
        Closes the socket and informs the other end that no more data will
        be sent
        """
        if self.connection == "CLOSED":
            print "ALREADY CLOSED"
            return 
        if self.connection != "ESTABLISHED":
            #SOMETHING WRONG, ERROR
            print "ERROR"
        # ----- SETTING ARB SEQ -----
        x = 76
        # ----- SEND FIN -----
        print 'SEND FIN'
        fin_mess = finMess(x)
        self.sock.sendto(fin_mess,self.addr)
        # ----- WAITING FOR ACK -----
        print 'WAIT FOR ACK'
        ack_mess, addr = self.sock.recvfrom(PKT)
        ack_mess = decodeMess(ack_mess)


