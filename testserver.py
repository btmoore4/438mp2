from transport import MP2Socket, MP2SocketError
from sender import PKT

port = 1111
filename = "tests/log.txt"
socket = MP2Socket()
f = open(filename, 'wb')
(client_host, client_port) = socket.accept(port)
print("testserver.py - Got connection from {}:{}".format(client_host, client_port))

while True:
    data = socket.recv(PKT)
    #print data
    if not data:
        break
    f.write(data)

f.close()
print "GETTING HERE"
socket.close()
print("Receiving successful")

