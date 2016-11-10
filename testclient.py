from transport import MP2Socket, MP2SocketError
import time

host = 'localhost'
port = 1111

print "testclient.py - Initiate Socket and Connection"
socket = MP2Socket()
socket.connect((host, port))
print "testclient.py - Begin sending"
socket.send("Woaaaaaah duddddddeee lolololololol")
socket.send("Woaaaaaah duddddddeee lolololololol")
socket.send("Woaaaaaah duddddddeee lolololololol")
time.sleep(2)
