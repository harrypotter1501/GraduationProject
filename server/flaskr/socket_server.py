# socket server

import socket
import threading
import struct

from queue import Queue
from functools import namedtuple

from io import BytesIO
from PIL import Image
import json


Sensors = namedtuple('Sensors', ['temperature', 'humidity'])
SocketBuffer = namedtuple('SocketBuffer', ['sensors', 'images'])

# socket thread class
class SocketThread(threading.Thread):
    ''' websocket thread '''

    def __init__(self, *args, **kwargs):
        self.buffer = SocketBuffer(
            json.dumps(Sensors('0', '0%')),
            Queue(5)
        )
        self.running = True
        return super().__init__(*args, **kwargs)


    def push_img(self, item):
        try:
            self.buffer.images.put_nowait(item)
        except:
            pass


    def pop_img(self):
        return self.buffer.images.get()


    def close(self):
        self.running = False
        self.join()


# socket server class
class SocketServer:
    ''' websocket server
    :singleton
    '''

    def __init__(self):
        ''' create a SocketServer instance
        :threads - a dict that stores all SocketThreads
        :DO NOT get new instance after initializiation
        '''

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        val = struct.pack('Q', 1000)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)

        self.s.bind(('127.0.0.1', 6000))#(('192.168.0.100', 8088))#
        self.s.listen(5)

        self.threads = {}
        self.address = {}
        self.bufsize = 100*1024


    # singleton
    @classmethod
    def instance(cls, *args, **kwargs):
        ''' one way to realize singleton '''

        if not hasattr(SocketServer, "_instance"):
            SocketServer._instance = SocketServer(*args, **kwargs)
        return SocketServer._instance


    # verify ip
    def verify_ip(self, ip):
        if ip == '127.0.0.1':
            return True
        return ip in [
            key.device_ip for key in self.threads.keys()
        ]


    # handler
    def socket_handler(self):
        ''' handler for socket thread '''

        conn, addr = self.s.accept()
        ip = addr[0]

        if not self.verify_ip(ip):
            print('IP {} unmatched'.format(ip))
            conn.close()
            return

        conn.send(b'Connection established\r\n')
        print('Accepted socket from {}'.format(ip))

        t = self.threads[ip]

        while t.running:
            try:
                data = conn.recv(self.bufsize)
            except Exception as e:
                continue
            #data = conn.recv(self.bufsize)

            if not data:
                break
            elif len(data) > 1000:
                img = Image.open(BytesIO(data))
                t.push_img(img)
                print('Qsize: {}'.format(t.buffer.images.qsize()))
            else:
                print('Recieved from {}: {}'.format(ip, data.decode()))

        conn.close()
        print('Socket {} closed'.format(ip))
        self.threads.pop(ip)


    # create new socket
    def create_socket(self, id, ip):
        ''' a method that creates a new websocket '''

        if ip in self.threads.keys():
            self.close_socket(ip)

        t = SocketThread(target=self.socket_handler)
        self.threads[ip] = t
        self.address[id] = ip

        t.start()
        return 'OK'


    # close a socket
    def close_socket(self, ip):
        ''' close a websocket '''

        try:
            self.threads[ip].close()
            return 'OK'
        except KeyError:
            return None


# interfaces
def init_server():
    ''' initialize the server '''

    return SocketServer.instance()


def create_socket(device_id, device_ip):
    ''' create a websocket that awaits connnection from specific ip '''

    return SocketServer.instance().create_socket(device_id, device_ip)


def get_thread(device_id):
    ''' get socket thread according to device_id '''

    try:
        ip = SocketServer.instance().address[device_id]
        t = SocketServer.instance().threads[ip]
    except KeyError:
        return None
    return t


def pop_img(device_id):
    ''' fetch a jpeg frame according to device_id '''

    t = get_thread(device_id)
    if t is not None:
        return t.pop_img()
    else:
        return None
