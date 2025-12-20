import json
import socket

# Default Parameters
HOST = "127.0.0.1"
PORT = 5555

class Reliable_server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with self.server_socket as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"listen on {self.host}:{self.port}")
            self.conn, self.address = s.accept()

    def accept_connection(self):
        with self.conn as server:
            raw_buffer = b""
            while True:
                chunk = server.recv(1024)
                if not chunk:
                    print("Client Disconnected")
                    break
                raw_buffer += chunk

                while b"\n" in raw_buffer:
                    line, _, raw_buffer = raw_buffer.partition(b"\n")

                    data = line.decode().strip()
                    if data == "SYN":
                        print(f"Accepted SYN from {self.address}, Sending SYN/ACK")
                        server.sendall(b"SYN/ACK\n")

                    elif data == "ACK":
                        print("Handshake Established (ACK received)")

def __main__():
    server = Reliable_server("127.0.0.1", 5555)
    server.accept_connection()
    print()

if __name__ == "__main__":
    __main__()