from transport import MP2Socket, MP2SocketError

host = 'localhost'
port = 1111

socket = MP2Socket()

socket.connect((host, port))
