import json
import socket

class Window:
    def __init__(self, buffer: list, size:int):
        self.window = buffer
        self.window_size = size

class Client:
    def __init__(self, host, port, timer=0, window=5,):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window = window

    def init_client(self):
        with self.client_socket as s:
            s.connect((self.host, self.port))
