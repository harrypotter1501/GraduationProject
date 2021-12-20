# some tests

import socket
import threading


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 8080))

s.listen(2)
print('listening...')
conn, _ = s.accept()

def blocked_socket_thread():
    global conn
    print('running...')
    while True:
        data = conn.recv(1024)
        print('Recv: {}'.format(data.decode()))

    conn.close()
    print('close')


t = threading.Thread(target=blocked_socket_thread)
t.start()

input()
conn.close()
