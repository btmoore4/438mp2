from helper import *

import socket
import threading
import thread

SEQ = 0
ACK = 1
SYN = 2
FIN = 3
LEN = 4
DATA = 5

PKT = 2048
PKT2 = 4
TIMEOUT = 10


class Sender:
    def __init__(self, sender_socket, initial_seq, recv_address):
        self.sock = sender_socket
        self.sock.setblocking(0)
        self.addr = recv_address 
        self.nextSeq = initial_seq
        self.sendBase = initial_seq
        self.buffer = []
        self.senderOpen = True 
        self.timerStart = False
        self.lock = threading.Lock()
        self.thread = thread.start_new_thread(self.start, ())

    def start(self):
        while self.senderOpen:
            if len(self.buffer) > 0: 
                data = self.pop()
                self.sock.sendto(dataMess(data, self.nextSeq), self.addr)
                self.nextSeq = self.nextSeq + len(data)
                if not self.timerStart:
                    self.timerStart = True
                    self.timer = threading.Timer(TIMEOUT, self.timeoutUpdate)
                    self.timer.start()
            try:
                raw_msg = self.sock.recv(2048)
                ack_msg = decodeMess(raw_msg)
                print ack_msg
                if ack_msg[ACK] > self.sendBase: 
                    self.sendBase = ack_msg[ACK]
                    print str(self.sendBase) + " -- " + str(self.nextSeq)
                    if self.sendBase == self.nextSeq: 
                        #All bytes ACKed
                        self.timer.cancel()
                        print "YEA"
                    else:
                        self.timer.cancel()
                        self.timer = threading.Timer(TIMEOUT, self.timeoutUpdate)
                        self.timer.start()
            except socket.error, e:
                pass

    def timeoutUpdate(self): 
        print "TIMEOUT"

    def send(self, data): 
        print "SENDING"
        self.add(data)

    def stop(self): 
        self.closed = True
        #finish getting all ACKS

    def add(self, data):
        self.lock.acquire()
        self.buffer.append(data) 
        self.lock.release()

    def pop(self):
        self.lock.acquire()
        data = self.buffer.pop(0)
        self.lock.release()
        return data


