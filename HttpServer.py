from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
address = ('127.0.0.1', 4009)
print 'server up on %s port %s' % address
serverSocket.bind(address)
serverSocket.listen(1)

while True:
    #Establish the connection
    print 'Ready to serve...'
    connectionSocket, addr = serverSocket.accept()
    print 'Connected via', addr

    try:
        message = connectionSocket.recv(1024)
        print 'Message is:', message
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()

        #Send one HTTP header line into socket
        connectionSocket.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        print 'OK Sent'
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i])
        connectionSocket.send("\r\n")
        connectionSocket.close()
    except IOError:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n")
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n")
        connectionSocket.close()
serverSocket.close()