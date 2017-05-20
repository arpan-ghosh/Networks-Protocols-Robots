from socket import *
from ssl import *
import sys
from pprint import pprint
import argparse
import sys
import certifi

if __name__ == '__main__':
    CA_CERT_PATH = 'server.crt'
    parser = argparse.ArgumentParser()

    tls_version = parser.add_mutually_exclusive_group()
    tls_version.add_argument("-tlsv1.0", "--tlsv1.0", dest="version", action= "store_const", const= PROTOCOL_TLSv1)
    # tls_version.add_argument("-tlsv1.1", "--tlsv1.1",dest="version", action= "store_const", const=PROTOCOL_TLSv1_1)
    # tls_version.add_argument("-tlsv1.2", "--tlsv1.2", dest="version", action= "store_const", const=PROTOCOL_TLSv1_2)
    tls_version.add_argument("-sslv3", "--sslv3", dest="version", action= "store_const", const= PROTOCOL_SSLv3)

    parser.add_argument("-ciphers", "--ciphers")
    parser.add_argument("-cacert", "--cacert", dest="cacert")
    parser.set_defaults(version= PROTOCOL_TLSv1, cacert=CA_CERT_PATH)
    parser.add_argument("server_host")
    parser.add_argument("server_port")
    parser.add_argument("filename") # unused arg because to test only GET /
     # not GET /filename as unspecified what GET is required

    args = parser.parse_args()
    print args
    # Create context will load using SSLContext.load_default_certs() if
    #   cafile is None
    ctx = create_default_context(purpose = Purpose.SERVER_AUTH, cafile=args.cacert)

    sock = socket(AF_INET, SOCK_STREAM)
    ssl_conn = wrap_socket(sock, cert_reqs=CERT_REQUIRED, ca_certs=args.cacert, ssl_version=args.version)
    target_host = args.server_host
    target_port = args.server_port
    ssl_conn.connect((target_host, int(target_port)))

    # get remote cert
    cert = ssl_conn.getpeercert()
    print("Checking server certificate")
    pprint(cert)
    if not cert or match_hostname(cert, target_host):
        raise Exception("Invalid SSL cert for host %s." %target_host )
    # print("Server certificate OK.\n Sending some custom request...GET ")
    ssl_conn.write(("GET /%s HTTP/1.1\r\n\r\n" % args.filename).encode())
    # print("Response received from server:")
    # print(ssl_conn.read())
    ssl_conn.close()
