from transport import MP2Socket, MP2SocketError
from sender import PKT
import time
import sys

host = 'localhost'
port = 1111
filename="tests/peter3.txt"
count = 0 
petertests[0] = "tests/peter.txt"
petertests[1] = "tests/peter.txt"
petertests[2] = "tests/peter.txt"

if len(sys.argv) == 2:
    host = sys.argv[0]
    filename = petertests[sys.argv[1]-1]
elif len(sys.argv) == 1:
    host = sys.argv[0]

print "testclient.py - Initiate Socket and Connection"
f = open(filename, 'rb')
socket = MP2Socket()
try:
    socket.connect((host, port))
except MP2SocketError:
    print("Error connecting to host")
    sys.exit(1)

print "testclient.py - Begin sending"
while True:
    data = f.read(PKT)
    count = count + len(data) 
    if not data:
        break
    socket.send(data)

f.close()
socket.close()
print("Sending successful")
print("Count = " + str(count))
