from helper import *
from timer import *
from sender import SEQ, ACK, SYN, FIN, LEN, DATA, PKT, TIMEOUT

import socket
import threading
import thread
import time


class Receiver:
    def __init__(self, recv_socket, initial_seq):
        self.sock = recv_socket
        self.seq = initial_seq
        self.acked = -1 
        self.receiverDone = False
        self.dataBuffer = None 
        self.bufferDone = False
        self.lock = threading.Lock()
        self.thread = thread.start_new_thread(self.start, ())

    def start(self):
        while True:
            raw_msg, send_addr = self.sock.recvfrom(PKT+50)
            #print raw_msg
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
		print self.acked
	
        ack_mess = ackMess(data_msg[SEQ]) 
        self.sock.sendto(ack_mess, send_addr)
	print "RECEIVER IS DONE"
        self.receiverDone = True

    def recv(self, length): 
        return self.pop(length)

    def stop(self): 
        while not self.bufferDone:
            time.sleep(0.1)
        time.sleep(1)
        print "STOPPING SOCKET"

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
        while len(self.dataBuffer) < length: 
            time.sleep(0.1)
            if self.receiverDone:
                self.lock.acquire()
                data = self.dataBuffer
                self.dataBuffer = ""
                self.lock.release()
                self.bufferDone = True
                return data
        self.lock.acquire()
        data = self.dataBuffer[0:length]
        self.dataBuffer = self.dataBuffer[length:]
        self.lock.release()
        return data

        """
        self.lock.acquire()
        if len(self.dataBuffer) > length:
            data = self.dataBuffer[0:length]
            self.dataBuffer = self.dataBuffer[length:]
        else:
            data = self.dataBuffer
            self.dataBuffer = ""
            if self.receiverDone:
                self.lock.release()
                self.bufferDone = True
                return data
        self.lock.release()
        return data
        """

