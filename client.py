import json
import socket
from typing import Any


class Window:
    def __init__(self, buffer: list, size:int):
        self.window = buffer
        self.window_size = size

class ReliableClient:
    def __init__(self, host, port, timer=0, window=5,):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window = window

    def init_client(self):
        with self.client_socket as s:
            s.connect((self.host, self.port))
            print("Sending SYN Request...")
            s.sendall(b"SYN\n")

            response = s.recv(1024).decode().strip()
            if response == "SYN/ACK":
                print("Accepted SYN/ACK from server, Sending ACK")
                s.sendall(b"ACK")
            else:
                print(f"Unexpected Response: {response}")



def __main__():
    client = ReliableClient("127.0.0.1", 5555)
    client.init_client()
    print()

if __name__ == "__main__":
    __main__()