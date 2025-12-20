import json
import socket

# Default Parameters
HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 1024

class Reliable_server:
    def __init__(self, host, port, conn):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.server_socket as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"listen on {self.host}:{self.port}")
            self.conn, address = s.accept()

    def accept_connection(self):
        with self.server_socket as s:
            s.recv

