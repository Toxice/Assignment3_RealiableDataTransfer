import json
import socket
from typing import Any


class Window:
    def __init__(self, buffer: list, size:int):
        self.window = buffer
        self.window_size = size


def build_payload(payload) -> str:
    packet = {
        "command": "PUSH",
        "content": payload
    }
    return json.dumps(packet)


class ReliableClient:
    def __init__(self, host, port, timer=0, window=5,):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.window = window
        self.connected = False
        self.ack_counter = 0

# 3 Way Handshake
    def init_client(self):
            self.client_socket.connect((self.host, self.port))
            print("Sending SYN Request...")
            self.client_socket.sendall(b"SYN\n")

            response = self.client_socket.recv(1024).decode().strip()
            if response == "SYN/ACK":
                print("Accepted SYN/ACK from server, Sending ACK")
                self.client_socket.sendall(b"ACK")
                self.connected = True
            else:
                print(f"Unexpected Response: {response}")
                print("Closing Connection...")
                self.client_socket.close()
                self.connected = False

    def send_message(self, message):
        payload = build_payload(message)
        data = payload.encode(encoding='utf-8') + b"\n"
        print(f"Sending PUSH: {message}")
        self.client_socket.sendall(data)



def __main__():
    client = ReliableClient("127.0.0.1", 5555)
    client.init_client()


if __name__ == "__main__":
    __main__()