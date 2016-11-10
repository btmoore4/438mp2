
class Sender:
    def __init__(self, sock, initSeq):
        self.sock = sock
        self.sock.setblocking(0)
        self.nextSeq = initSeq
        self.sendBase = initSeq
        self.closed = False
        self.buffer = []
        self.lock = threading.Lock()
        self.timer = threading.Timer(TIMEOUT, self.timeoutUpdate)

    def start():
        while self.closed == False:
            if self.buffer: 
                data = self.buffer.pop(0)
                self.sock.sendto(,addr)
                self.nextSeq = self.nextSeq + len(data)
            try:
                msg = self.sock.recv(4096)
                if ack_num > self.sendBase: 
                    self.sendBase = ack_num
                    if self.sendBase == self.nextSeq: 
                        #Stop Timer
                    else: 
                        #start Timer
            except socket.timeout, e:

    def timeoutUpdate(): 

    def send(data): 
        self.lock.acquire()
        self.buffer.append(data) 
        self.lock.release()

    def stop(): 
        self.closed = True
