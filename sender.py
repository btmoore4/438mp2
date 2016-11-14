from helper import *
from timer import *

import socket
import threading
import thread
import time

#DEFINED
SEQ = 0
ACK = 1
SYN = 2
FIN = 3
LEN = 4
DATA = 5

PKT = 50
TIMEOUT = 10


class Sender:
    def __init__(self, sender_socket, initial_seq, recv_address):
        self.sock = sender_socket
        self.sock.setblocking(0)
        self.addr = recv_address 
        self.nextSeq = initial_seq
        self.sendBase = initial_seq
        self.sendBuffer = []
        self.noACK = {}
        self.senderOpen = True 
        self.senderDone = False
        self.timer = TCPTimeout(TIMEOUT, self.timeoutUpdate)
        self.lock = threading.Lock()
        self.thread = thread.start_new_thread(self.start, ())

    def start(self):
        while True:
            if len(self.sendBuffer) > 0: 
                data = self.pop()
                data_mess = dataMess(data, self.nextSeq)
                self.sock.sendto(data_mess, self.addr)
                #print data_mess
                self.nextSeq = self.nextSeq + len(data)
                self.noACK[self.nextSeq] = data_mess
                self.timer.runFirst()
            try:
                raw_msg = self.sock.recv(PKT)
                ack_msg = decodeMess(raw_msg)
                #print ack_msg
                self.noACK.pop(ack_msg[ACK], None)
                if ack_msg[ACK] > self.sendBase: 
                    self.sendBase = ack_msg[ACK]
                    if self.sendBase == self.nextSeq: 
                        self.timer.stop()
                        if not self.senderOpen and len(self.sendBuffer) == 0: 
                            break
                    else:
                        self.timer.start()
            except socket.error, e:
                #Should just be no message received
                pass
        print "SOCKET IS DONE SENDING"
        self.sock.setblocking(1)
        while True: 
            fin_mess = finMess(self.nextSeq)
            self.sock.sendto(fin_mess, self.addr)
            raw_msg, addr = self.sock.recvfrom(PKT)
            ack_mess = decodeMess(raw_msg)
            if ack_mess[ACK] == self.nextSeq + 1:
                break
        self.senderDone = True

    def timeoutUpdate(self): 
        print "TIMEOUT - RESENDING UNACKED MESSAGE"
        data = self.noACK[sorted(self.noACK, key=self.noACK.get)[0]]
        self.sock.sendto(data, self.addr)

    def send(self, data): 
        self.add(data)

    def stop(self): 
        self.senderOpen = False
        while not self.senderDone:
            time.sleep(0.1)
        print "STOPPING SOCKET"

    def add(self, data):
        self.lock.acquire()
        self.sendBuffer.append(data) 
        self.lock.release()

    def pop(self):
        self.lock.acquire()
        data = self.sendBuffer.pop(0)
        self.lock.release()
        return data



