from socket import socket

import ssl

from pprint import pprint

TARGET_HOST ='localhost'

TARGET_PORT = 8000

CA_CERT_PATH = "/etc/ssl/certs/ca-bundle.crt"

if __name__ == '__main__':

    sock = socket()

    ssl_conn = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1, ca_certs=CA_CERT_PATH)

    target_host = TARGET_HOST

    target_port = TARGET_PORT

    ssl_conn.connect((target_host, int(target_port)))

    # get remote cert

    cert = ssl_conn.getpeercert()

    print("Checking server certificate")

    pprint(cert)

    if not cert or ssl.match_hostname(cert, target_host):

        raise Exception("Invalid SSL cert for host %s. Check if this is a man-in-the-middle attack!" %target_host )

    print("Server certificate OK.\n Sending some custom request... GET ")

    ssl_conn.write('GET / \n'.encode('utf-8'))

    print("Response received from server:")

    print(ssl_conn.read())

    ssl_conn.close()

