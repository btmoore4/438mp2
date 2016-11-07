from socket import *
from helper import *
"""
Implements the MP2 socket class, as described below
"""
SEQ = 0
ACK = 1
SYN = 2
FIN = 3

class MP2SocketError(Exception):
    """ Exception base class for protocol errors """
    pass

class MP2Socket:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.connection = "INIT"
        self.addr = ("",0)

    def connect(self, addr):
        """
        Connects to a remote MP2 transport server. Address is specified by a
        pair `(host,port)`, where `host` is a string with either an IP address
        or a hostname, and `port` is a UDP port where data will arrive

        A client must call `connect` as the first operation on the socket.

        This call raises MP2SocketError if a connection cannot be established.
        It does not return any value on success
        """
        # ----- SETTING ARB SEQ -----
        x = 108
        # ----- SEND SYN -----
        print 'SEND SYN'
        syn_mess = synMess(x)
        self.sock.sendto(syn_mess.encode(),addr)
        # ----- WAITING FOR SYNACK -----
        print 'WAITING FOR SYNACK'
        synack_mess, serverAddress = self.sock.recvfrom(2048)
        synack_mess = decodeMess(synack_mess.decode())
        # ----- IF INCORRECT SYNACK -----
        if synack_mess[SYN] != 1 or synack_mess[ACK] != x + 1:
            print "NOT RIGHT SYNACK"
            #EXCEPTION
        # ----- SEND ACK -----
        print 'SEND ACK'
        ack_mess = ackMess(synack_mess[SEQ]) 
        self.sock.sendto(ack_mess.encode(),addr)
        print "CONNECTION ESTABLISHED"
        self.connection = "ESTABLISHED"
        self.addr = addr

    def accept(self, port):
        """
        Waits for a connection on a given (UDP) port. Returns a pair
        `(host,port)` representing the client address.

        A server must call `accept` as the first operation on the socket.

        Raises MP2SocketError if an error is encountered (e.g., UDP port
        already in use)
        """
        # ----- SETTING ARB SEQ -----
        y = 47
        # ----- WAITING FOR SYN -----
        print 'WAITING FOR SYN'
        self.sock.bind(('', port))
        syn_mess, clientAddress = self.sock.recvfrom(2048)
        syn_mess = decodeMess(syn_mess.decode())
        # ----- IF MESS IS NOT SYN -----
        if syn_mess[SYN] != 1:
            print "NOT A SYN MES"
            #EXCEPTION
        # ----- SEND SYN_ACK -----
        print 'SEND SYN_ACK' 
        synack_mess = synackMess(y, syn_mess[SEQ]) 
        self.sock.sendto(synack_mess.encode(),clientAddress)
        # ----- WAIT FOR ACK -----
        print 'WAIT FOR ACK'
        ack_mess, clientAddress = self.sock.recvfrom(2048)
        ack_mess = decodeMess(ack_mess.decode())
        # ----- IF INCORRECT ACK -----
        if ack_mess[ACK] != y + 1:
            print "INCORRECT ACK"
            #EXCEPTION
        print "CONNECTION ESTABLISHED"
        self.connection = "ESTABLISHED"
        self.addr = clientAddress
        return clientAddress

    def send(self, data):
        """
        Send data to the remote destination. Data may be of arbitrary length
        and should be split into smaller packets. This call should block
        for flow control, though you can buffer some small amount of data.
        This call should behave like `sendall` in Python; i.e., all data must
        be sent. Does not return any value.

        Should be called on a socket after connect or accept
        """
        self.connection = "ESTABLISHED"
        pass

    def recv(self, length):
        """
        Receive data from the remote destination. Should wait until data
        is available, then return up to `length` bytes. Should return "" when
        the remote end closes the socket
        """
        pass

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
        self.sock.sendto(fin_mess.encode(),self.addr)
        # ----- WAITING FOR ACK -----
        print 'WAIT FOR ACK'
        ack_mess, addr = self.sock.recvfrom(2048)
        ack_mess = decodeMess(ack_mess.decode())
     
 

        pass
