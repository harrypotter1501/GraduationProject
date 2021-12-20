# some other tests

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8080))
print('connected!')

s.send(b'someting')
while not input():
    pass

s.close()
