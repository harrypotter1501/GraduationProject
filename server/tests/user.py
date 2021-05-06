# self defined tests

import socket
from PIL import Image
from io import BytesIO

from threading import Thread
import time


frame = 0
size = 0
stop = False

def timer():
    global frame, size, stop
    while not stop:
        size = size/frame/1024 if frame != 0 else 0
        print('Frame: {}/s, Average image size: {}k'.format(frame, size))
        frame = 0
        size = 0
        time.sleep(1)


t = Thread(
    target=timer
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('192.168.0.103', 8088))
s.listen(2)
print('Listening...')

conn, addr = s.accept()
print('Connected!')
conn.send(b'Connected!')

t.start()

while True:
    try:
        data = conn.recv(100*1024)
    except:
        stop = True
        break

    frame += 1
    size += len(data)
    if not data:
        stop = True
        break

conn.close()
t.join()
print('Connection closed')
