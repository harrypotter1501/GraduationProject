# another user defined test

import socket
import time
import requests


with open('tests/demo.jpg', 'rb') as f:
    img = f.read()

res = requests.get(
    'http://127.0.0.1:8080/device/?device_id=test&device_key=123456'
)
print(res)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 6000))
data = s.recv(20)
print(data.decode())

while not input(':'):
    s.send(img)
    print('send')

s.close()
