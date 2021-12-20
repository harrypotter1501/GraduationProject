# another user defined test

import os
import socket
import time
import requests
import threading


def gen_img():
    base = 'c:/Users/lenovo/Desktop/graduate/stream/'
    img_lst = os.listdir(base)
    img_lst.sort(key=lambda x: int(x.split('.')[0]))
    
    while True:
        for img in img_lst:
            with open(os.path.join(base, img), 'rb') as f:
                yield f.read()


def recv_thread(s):
    while True:
        data = s.recv(1024)
        if not data:
            break
        try:
            print('Recved:', int(data.decode()))
        except:
            pass


def send_thread(s):
    for img in gen_img():
        s.send(img)
        time.sleep(0.2)


def main_thread(s):
    rt = threading.Thread(
        target=recv_thread,
        args=(s,)
    )
    rt.setDaemon(True)

    st = threading.Thread(
        target=send_thread,
        args=(s,)
    )
    st.setDaemon(True)

    rt.start()
    st.start()

    input()
    s.close()


if __name__ == '__main__':
    res = requests.get(
        'http://127.0.0.1:8080/device/?device_id=test_sys&device_key=abcdef'
    )
    print(res)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8088))
    print('Connection success!')
    print('From Server:', s.recv(30).decode())

    threading.Thread(
        target=main_thread,
        args=(s,)
    ).start()
