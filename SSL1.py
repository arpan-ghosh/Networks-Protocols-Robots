import socket
import ssl
from pprint import pprint

HOSTNAME = "www.python.org"


context = ssl.create_default_context()
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname=True
context.load_verify_locations("/etc/ssl/certs/ca-bundle.crt")
conn = context.wrap_socket(socket.socket(socket.AF_INET),server_hostname=HOSTNAME)
conn.connect((HOSTNAME,443))
cert = conn.getpeercert()

#pprint(cert)

conn.sendall(b"HEAD /HTTP/1.0\r\nHost:www.python.org\r\n\r\n")

cert = conn.recv(1024).split(b"\r\n")

pprint(cert)