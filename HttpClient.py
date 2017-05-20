from socket import *
import sys

server_host = sys.argv[-3]
server_port = int(sys.argv[-2])
filename = sys.argv[-1]

clientSocket = socket(AF_INET, SOCK_STREAM)

server = (server_host, server_port)
print 'connecting to %s port %s' % server

clientSocket.connect(server)

try:
    clientSocket.send("GET /HelloWorld.html HTTP/1.0\n\n")

    while True:
        data = clientSocket.recv(1024)
        if data == "": break
        print 'received "%s"' % data,

except IOError:
    print "IOError"
    clientSocket.close()

finally:
    print "closing client socket"
    clientSocket.close()