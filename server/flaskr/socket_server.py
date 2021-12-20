# socket server

import time
import socket
import threading
import struct

from queue import Queue
from functools import namedtuple

from io import BytesIO
from PIL import Image
import json


SensorsPop = namedtuple('SensorsPop', ['temperature', 'humidity', 'time'])
SocketBuffer = namedtuple('SocketBuffer', ['sensors', 'images'])


class Sensors:
    ''' buffer for sensor data '''

    def __init__(self):
        self.temperature = 0
        self.humidity = 0
        self.time = 0


    def set(self, temp=0, humid=0):
        self.temperature = temp
        self.humidity = humid
        self.time = time.time()


    def get(self):
        return SensorsPop(
            self.temperature,
            self.humidity,
            self.time
        )


# socket thread class
class SocketThread(threading.Thread):
    ''' websocket thread '''

    def __init__(self, *args, **kwargs):
        self.buffer = SocketBuffer(
            Sensors(),
            Queue(5)
        )
        self.running = True
        self.conn = None
        return super().__init__(*args, **kwargs)


    def push_img(self, item):
        try:
            self.buffer.images.put_nowait(item)
        except:
            pass


    def pop_img(self):
        return self.buffer.images.get_nowait()


    def push_sensors(self, temp=0, humid=0):
        self.buffer.sensors.set(temp, humid)


    def pop_sensors(self):
        return self.buffer.sensors.get()


    def close(self):
        self.running = False


# socket server class
class SocketServer:
    ''' websocket server
    :singleton
    '''

    def __init__(self, ip='127.0.0.1', port=6000, bufsize_k=500):
        ''' create a SocketServer instance
        :threads - a dict that stores all SocketThreads
        :DO NOT get new instance after initializiation
        '''

        #socket.setdefaulttimeout(5)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.s.bind((ip, port))
        self.s.listen(5)

        self.threads = {}
        self.address = {}
        self.bufsize = bufsize_k * 1024

        self.handler_timeout = 0.1
        self.connect_timeout = 5


    # singleton
    @classmethod
    def instance(cls, *args, **kwargs):
        ''' one way to realize singleton '''

        if not hasattr(SocketServer, "_instance"):
            SocketServer._instance = SocketServer(*args, **kwargs)
        return SocketServer._instance


    # verify ip
    def verify_ip(self, ip):
        return ip in [
            key for key in self.threads.keys()
        ]


    # refresh
    def refresh_handler(self, t):
        ''' handles data recieving
        :a sub-thread of main
        '''

        while t.running:
            try:
                data = t.conn.recv(self.bufsize)
            except WindowsError as win_err:
                print(win_err)
                break
            except Exception as e:
                #print(e)
                continue
            #data = t.conn.recv(self.bufsize)

            if not data:
                break
            elif len(data) > 10:
                try:
                    img = Image.open(BytesIO(data))
                    t.push_img(img)
                    #print('Qsize: {}'.format(t.buffer.images.qsize()))
                except Exception as e:
                    print(e)
                    print(data[:10], '...')
                    continue
            else:
                try:
                    temp, humid = map(int, data.decode().strip('\r\n').split())
                    t.push_sensors(temp, humid)
                except Exception as e:
                    print(e)
                    continue


    # handler
    def socket_handler(self):
        ''' handler for socket thread '''

        self.s.settimeout(5)
        try:
            conn, addr = self.s.accept()
        except Exception as e:
            print(e)
            return

        self.s.settimeout(None)
        ip = addr[0]

        if not self.verify_ip(ip):
            print('IP {} unmatched'.format(ip))
            conn.close()
            return

        conn.send(b'Connection established\r\n')
        print('Accepted socket from {}'.format(ip))

        t = self.threads[ip]
        t.conn = conn

        subt = threading.Thread(
            target=self.refresh_handler,
            args=(t,)
        )

        subt.setDaemon(True)
        subt.start()
        while t.running:
            subt.join(timeout=self.handler_timeout)

        conn.close()
        print('Socket {} closed'.format(ip))
        self.threads.pop(ip)


    # create new socket
    def create_socket(self, dev_id, dev_ip):
        ''' a method that creates a new websocket '''

        if dev_ip in self.threads.keys():
            self.close_socket(dev_id)

        t = SocketThread(target=self.socket_handler)
        self.threads[dev_ip] = t
        self.address[dev_id] = dev_ip
        #t.setDaemon(True)

        t.start()
        print('Socket created for {}: {}'.format(dev_id, dev_ip))
        return 'OK'


    # close a socket
    def close_socket(self, dev_id):
        ''' close a websocket '''

        try:
            ip = self.address[dev_id]
            t = self.threads[ip]
            t.close()
            t.join()
            return 'OK'
        except KeyError:
            return None


# interfaces
def init_server(ip, port):
    ''' initialize the server '''

    return SocketServer.instance(ip, port)


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
    if t:
        return t.pop_img()
    else:
        return None


def pop_sensors(device_id):
    ''' fetch sensor data according to device_id '''

    t = get_thread(device_id)
    if t:
        return t.pop_sensors()
    else:
        return None


def send_command(device_id, cmd):
    ''' send a command to device '''

    t = get_thread(device_id)
    if t and t.conn:
        t.conn.send(cmd.to_bytes(
            length=1,
            byteorder='little',
            signed=False
        ))
        return 'OK'
    else:
        return None


def close_socket(device_id):
    ''' close a websocket '''

    return SocketServer.instance().close_socket(device_id)


def socket_alive(device_id):
    ''' check if a socket is alive for specific device id '''

    t = get_thread(device_id)
    return True if t else False
