import json
import socket

# Default Parameters
HOST = "127.0.0.1"
PORT = 5555

class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # 1st step - connect to a TCP socket
    def init_socket(self):
        """
        init TCP socket
        :param self: TCP Socket
        """
        with self.server_socket as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"listen on {self.host}:{self.port}")
            conn, address = s.accept()


