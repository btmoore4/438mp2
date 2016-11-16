import threading 

class TCPTimeout:
    def __init__(self, time, func):
        self.timeout = time
        self.func = func
        self.timer = None
        self.running = False

    def setTIMEOUT(self, time):
        self.timeout = time

    def callBack(self):
        self.func()
        self.running = False
        self.runFirst()

    def start(self):
        self.stop()
        self.runFirst()

    def stop(self):
        if not self.running:
            return
        self.timer.cancel()
        self.running = False

    def runFirst(self):
        if self.running:
            return
        self.timer = threading.Timer(self.timeout, self.callBack)
        self.running = True
        self.timer.start()
