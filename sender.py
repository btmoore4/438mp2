from helper import *
from timer import *

import socket
import threading
import thread
import time
import sys

#DEFINED
SEQ = 0
ACK = 1
SYN = 2
FIN = 3
LEN = 4
DATA = 5

PKT = 2048
TIMEOUT = 4
TEST_RTT = 1 


class Sender:
    def __init__(self, sender_socket, initial_seq, recv_address, rtt):
        self.sock = sender_socket
        self.sock.setblocking(0)
        self.init = initial_seq
        self.addr = recv_address 
        self.nextSeq = initial_seq
        self.sendBase = initial_seq
        self.sendBuffer = []
        self.estRTT = rtt 
        self.devRTT = 2*rtt 
        self.noACK = {}
        self.senderOpen = True 
        self.senderDone = False
        self.timer = TCPTimeout(self.estRTT + self.devRTT + TEST_RTT, self.timeoutUpdate)
        self.lock = threading.Lock()
        self.lock_noACK = threading.Lock()
        self.thread = thread.start_new_thread(self.start, ())
        self.recvBuff = 2048*16 
        self.timeOutPrint = []

    def resendFIN(self):
        print "RESEND FIN"
        fin_mess = finMess(self.nextSeq)
        self.sock.sendto(fin_mess, self.addr)

    def start(self):
        while True:
            if len(self.sendBuffer) > 0: 
                if self.nextSeq - self.sendBase > self.recvBuff: 
                    pass
                else:
                    data = self.pop()
                    data_mess = dataMess(data, self.nextSeq)
                    self.sock.sendto(data_mess, self.addr)
                    #print data_mess
                    self.nextSeq = self.nextSeq + len(data)
                    self.lock_noACK.acquire()
                    self.noACK[self.nextSeq] = data_mess
                    self.lock_noACK.release()
                    self.timer.runFirst()
            try:
                raw_msg = self.sock.recv(PKT)
                ack_msg = decodeMess(raw_msg)
                #print ack_msg
                self.lock_noACK.acquire()
                self.noACK.pop(ack_msg[ACK], None)
                self.lock_noACK.release()
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
        print 
        while True: 
            fin_mess = finMess(self.nextSeq)
            self.sock.sendto(fin_mess, self.addr)
            self.finTimer = TCPTimeout(3, self.resendFIN) 
            self.finTimer.start()
            raw_msg, addr = self.sock.recvfrom(PKT)
            self.finTimer.stop()
            ack_mess = decodeMess(raw_msg)
            if ack_mess[ACK] == self.nextSeq + 1:
                break
        self.senderDone = True

    def timeoutUpdate(self): 

        if len(self.timeOutPrint) == 8:
            sys.stderr.write('stderr - SENDER TIMEOUT: '+str(self.timeOutPrint[0])+"-"+str(self.sendBase)+'\n')
            self.timeOutPrint = []
        else:
            self.timeOutPrint.append(self.sendBase)

        self.lock_noACK.acquire()
	sort_list = self.noACK.keys()
	if sort_list:
	    sort_list.sort()
	    for key in sort_list:	
            	data = self.noACK[key]
            	self.sock.sendto(data, self.addr)
        self.lock_noACK.release()

    def send(self, data): 
        self.add(data)

    def stop(self): 
        self.lock.acquire()
        self.senderOpen = False
        self.lock.release()
        while not self.senderDone:
            time.sleep(0.1)
        print "STOPPING SOCKET"
        print self.nextSeq - self.init

    def add(self, data):
        self.lock.acquire()
        self.sendBuffer.append(data) 
        self.lock.release()

    def pop(self):
        self.lock.acquire()
        data = self.sendBuffer.pop(0)
        self.lock.release()
        return data

