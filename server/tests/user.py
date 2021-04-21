# self defined tests

import socket
from PIL import Image
from io import BytesIO


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.settimeout()

s.bind(('127.0.0.1', 6000))
s.listen(2)
print('Listening...')

conn, addr = s.accept()
print('Connected!')
conn.send(b'Connected!')

s.setblocking(False)

while True:
    try:
        data = conn.recv(100*1024)
    except:
        continue

    print('Data Recieved from {}:'.format(addr))
    print('Length: {}'.format(len(data)))
    if not data:
        break

conn.close()
