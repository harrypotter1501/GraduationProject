# self defined tests

import socket
from PIL import Image
from io import BytesIO


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
name = socket.gethostname()
addr = socket.gethostbyname(name)
print(addr)
s.bind(('192.168.0.100', 8088))
s.listen(2)
print('Listening...')

conn, addr = s.accept()
print('Connected!')

while True:
    data = conn.recv(10*1024)
    print('Data Recieved from {}:'.format(addr))
    print('Length: {}'.format(len(data)))
    bs = BytesIO(data)
    img = Image.open(bs)
    img.show()
    conn.send(bytes('Server recieved {} bits\r\n'.format(len(data)), encoding='utf8'))
