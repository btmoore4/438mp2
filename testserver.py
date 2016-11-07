from transport import MP2Socket, MP2SocketError

port = 1111
socket = MP2Socket()
(client_host, client_port) = socket.accept(port)
