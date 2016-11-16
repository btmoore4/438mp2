from helper import *
from timer import *
from sender import SEQ, ACK, SYN, FIN, LEN, DATA, PKT, TIMEOUT

import socket
import threading
import thread
import time
import sys


class Receiver:
    def __init__(self, recv_socket, initial_seq, start_data, start_send_addr):
        self.sock = recv_socket
        self.seq = initial_seq
        self.init = initial_seq
        self.acked = -1 
        self.dataBuffer = ""
        self.receiverDone = False
        self.bufferDone = False
        self.bufferNotEmpty = False
        self.count = 0
        self.final = -1
        self.lock = threading.Lock()
        self.start_data = start_data
        self.start_addr = start_send_addr
        self.thread = thread.start_new_thread(self.start, ())

    def start(self):
        while True:
            if self.start_data:
                send_addr = self.start_addr
                data_msg = self.start_data
                self.start_data = None
            else:
                raw_msg, send_addr = self.sock.recvfrom(PKT+50)
                data_msg = decodeMess(raw_msg)
            if data_msg[FIN] == 1:
                break
            if self.acked < 0: 
                self.init = data_msg[SEQ]
                self.acked = data_msg[SEQ] + data_msg[LEN]
                ack_mess = ackDataMess(self.seq, data_msg[SEQ] + data_msg[LEN]) 
                self.sock.sendto(ack_mess, send_addr)
                self.add(data_msg[DATA])
                self.bufferNotEmpty = True
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
        self.final = self.acked - self.init
        sys.stderr.write('stderr - RECEIVER IS DONE\n')
        sys.stderr.write('srderr - Total Received: ' + str(self.final) + "\n")
        sys.stderr.write('stderr - count so far: ' + str(self.count) + '\n')
        self.receiverDone = True

        while True:
            self.lock.acquire()
            if len(self.dataBuffer) < 1:
                self.lock.release()
                break
            self.lock.release()
            time.sleep(0.1)

        sys.stderr.write('stderr -BUFFER IS DONE\n')
        self.bufferDone = True

    def receiver_recv(self, length): 
        recv_data = self.pop(length)
        self.count = self.count + len(recv_data)
        if recv_data == "":
            sys.stderr.write('stderr - RECV nothing\n')
        if recv_data == None:
            sys.stderr.write('stderr - RECV none\n')
        return recv_data

    def receiver_stop(self): 
        sys.stderr.write('stderr - STOPPING SOCKET\n')
        sys.stderr.write('stderr - count: ' + str(self.count) + '\n')
        while not self.bufferDone:
            time.sleep(0.1)
        time.sleep(1)
        sys.stderr.write('stderr - STOPPED SOCKET\n')

    def add(self, data):
        self.lock.acquire()
        if len(self.dataBuffer) > 0:
            self.dataBuffer = self.dataBuffer + data
        else:
            self.dataBuffer = data
        self.lock.release()

    def pop(self, length):
        while not self.bufferNotEmpty:
            time.sleep(0.1)
        while True:
            self.lock.acquire()
            if len(self.dataBuffer) > length:
                data = self.dataBuffer[:length]
                rem_data = self.dataBuffer[length:]
                self.dataBuffer = rem_data
                self.lock.release()
                return data
            if self.receiverDone and len(self.dataBuffer) <=length:
                data = self.dataBuffer
                self.dataBuffer = ""
                self.lock.release()
                return data
            self.lock.release()
            time.sleep(0.1)
