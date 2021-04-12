# socket server

import socket
import threading

from queue import Queue
from PIL import Image
from io import BytesIO


# socket thread class
class SocketThread(threading.Thread):
    ''' websocket thread '''

    def __init__(self, *args, **kwargs):
        self.buffer = Queue(5)
        self.last_item = None
        self.running = True
        return super().__init__(*args, **kwargs)


    def push_img(self, item):
        if self.buffer.full():
            self.buffer.get()
        self.buffer.put(item)


    def pop_img(self):
        if not self.buffer.empty():
            self.last_item = self.buffer.get()
        return self.last_item


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
        #ip = socket.gethostbyname(socket.gethostname())
        self.s.bind(('127.0.0.1', 6000))#(('192.168.0.100', 8088))#
        self.s.listen(5)

        self.threads = {}
        self.address = {}
        self.bufsize = 10*1024


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
        for key in self.threads.keys():
            if ip == key.device_ip:
                return True
        return False


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
                print(e)
                break

            if not data:
                break

            stream = BytesIO(data)
            img = Image.open(stream)
            t.push_img(img)

            info = 'Socket recieved {} bits'.format(len(data))
            print(info)

        conn.close()
        print('Socket {} closed'.format(ip))
        self.threads.pop(ip)


    # create new socket
    def create_socket(self, ip):
        ''' a method that creates a new websocket '''

        if ip in self.threads.keys():
            t = self.threads[ip]
            t.running = False
            t.join()
            self.threads.pop(ip)

        t = SocketThread(
            target=self.socket_handler
        )
        self.threads[ip] = t
        t.start()
        return 'OK'


# init server
def init_server():
    ''' initialize the server '''

    return SocketServer.instance()


def create_socket(device_id, device_ip):
    ''' create a websocket that awaits connnection from specific ip '''

    SocketServer.instance().address[device_id] = device_ip
    return SocketServer.instance().create_socket(device_ip)


def close_socket(device_id):
    ''' close a websocket '''

    pass


def get_socket_buffer(device_id):
    ''' get socket buffer according to device_id '''

    try:
        ip = SocketServer.instance().address[device_id]
        t = SocketServer.instance().threads[ip]
    except KeyError:
        return {'errmsg': 'Login required'}
    return t
