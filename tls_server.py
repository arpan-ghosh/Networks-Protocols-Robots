import socket
import ssl
from ssl import *
from pprint import pprint
from _ssl import *
import argparse
import sys
import certifi

SSL_SERVER_PORT = 8006 # 443 appears to be reserved on my computer

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    tls_version = parser.add_mutually_exclusive_group()
    tls_version.add_argument("-tlsv1.0", "--tlsv1.0", dest="version", action= "store_const", const= PROTOCOL_TLSv1)
    tls_version.add_argument("-tlsv1.1", "--tlsv1.1",dest="version", action= "store_const", const=PROTOCOL_TLSv1_1)
    tls_version.add_argument("-tlsv1.2", "--tlsv1.2", dest="version", action= "store_const", const=PROTOCOL_TLSv1_2)
    tls_version.add_argument("-sslv3", "--sslv3", dest="version", action= "store_const", const= PROTOCOL_SSLv3)
    parser.set_defaults(version= PROTOCOL_TLSv1)
    args = parser.parse_args()

    serverSocket = socket()
    serverSocket.bind(('', SSL_SERVER_PORT))
    serverSocket.listen(5)

    print("Live on port %s" %SSL_SERVER_PORT)

    print ('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    ssl_conn = ssl.wrap_socket(connectionSocket, server_side=True, certfile='server.crt', keyfile='server.key', ssl_version=args.version)
    try:
        message = ssl_conn.read()
        print (message)
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        # Send one HTTP header line into socket
        outstr = 'HTTP/1.1 200 OK\n\n'
        print (outputdata)
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            outstr += outputdata[i]
        ssl_conn.write(outstr.encode())
        ssl_conn.close()
    except IOError:
        # Send response message for file not found
        data = open("404.html").read()
        ssl_conn.write('HTTP/1.1 404 Not Found\n\n'.encode())
        #Close client socket
        ssl_conn.close()

serverSocket.close()
