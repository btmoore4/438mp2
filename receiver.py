from helper import *
from timer import *
from sender import SEQ, ACK, SYN, FIN, LEN, DATA, PKT, TIMEOUT

import socket
import threading
import thread
import time
import sys


class Receiver:
    def __init__(self, recv_socket, initial_seq):
        self.sock = recv_socket
        self.seq = initial_seq
        self.acked = -1 
        self.init = initial_seq
        self.receiverDone = False
        self.dataBuffer = None 
        self.bufferDone = False
        self.lock = threading.Lock()
        self.thread = thread.start_new_thread(self.start, ())

    def start(self):
        while True:
            raw_msg, send_addr = self.sock.recvfrom(PKT+50)
            data_msg = decodeMess(raw_msg)
            if data_msg[FIN] == 1:
                break
            if self.acked < 0: 
                self.acked = data_msg[SEQ] + data_msg[LEN]
                ack_mess = ackDataMess(self.seq, data_msg[SEQ] + data_msg[LEN]) 
                self.sock.sendto(ack_mess, send_addr)
                self.add(data_msg[DATA])
            elif self.acked == data_msg[SEQ]:
                ack_mess = ackDataMess(self.seq, data_msg[SEQ] + data_msg[LEN]) 
                self.sock.sendto(ack_mess, send_addr)
                self.add(data_msg[DATA])
                self.acked = self.acked + data_msg[LEN]
            else:
                ack_mess = ackDataMess(self.seq, self.acked) 
                self.sock.sendto(ack_mess, send_addr)
	    #print self.acked
	
        ack_mess = ackMess(data_msg[SEQ]) 
        self.sock.sendto(ack_mess, send_addr)
	print "RECEIVER IS DONE"
        sys.stderr.write('stderr - RECEIVER IS DONE\n')
        sys.stderr.write(str(self.acked) + "\n")
        self.receiverDone = True

    def recv(self, length): 
        return self.pop(length)

    def stop(self): 
        sys.stderr.write('stderr - TRYING TO STOPPING SOCKET\n')
        while not self.bufferDone:
            time.sleep(0.1)
        time.sleep(1)
        print "STOPPING SOCKET"
        sys.stderr.write('stderr - STOPPING SOCKET\n')

    def add(self, data):
        self.lock.acquire()
        if self.dataBuffer:
            self.dataBuffer = self.dataBuffer + data
        else:
            #print data
            self.dataBuffer = data
        self.lock.release()

    def pop(self, length):
        if self.bufferDone:
            return None
        while not self.dataBuffer:
            time.sleep(0.1)
            if self.receiverDone:
		break
        self.lock.acquire()
        while len(self.dataBuffer) <= length: 
            self.lock.release()
            time.sleep(0.1)
            if self.receiverDone:
                sys.stderr.write('stderr - GETTING TO BUFFER DONE\n')
                self.lock.acquire()
                data = self.dataBuffer
                self.dataBuffer = ""
                self.lock.release()
                self.bufferDone = True
                sys.stderr.write('stderr - BUFFER DONE\n')
                return data
            self.lock.acquire()
        data = self.dataBuffer[0:length]
        self.dataBuffer = self.dataBuffer[length:]
        self.lock.release()
        return data

