import json
import socket
import time
import os


def load_client_config():
    """
    Prompts user to load config from file or manual input.
    Returns a dictionary of parameters and the ACTUAL file content to send.
    """
    config = {
        "message_path": "",
        "window_size": 5,
        "timeout": 3
    }

    print("--- Client Configuration ---")
    mode = input("Load from file (f) or manual input (m)? ").strip().lower()

    if mode == 'f':
        filename = input("Enter config file path (default: client_config.txt): ").strip() or "client_config.txt"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip().replace('"', '')  # Remove quotes if present

                        if key == "message":
                            config["message_path"] = val
                        elif key == "window_size":
                            config["window_size"] = int(val)
                        elif key == "timeout":
                            config["timeout"] = int(val)
            print("Loaded config from file.")
        else:
            print("Config file not found!")
            return None
    else:
        # Manual Input
        config["message_path"] = input("Enter path of file to send: ").strip().replace('"', '')
        try:
            config["window_size"] = int(input("Enter Window Size: "))
            config["timeout"] = int(input("Enter Timeout (seconds): "))
        except ValueError:
            print("Invalid numbers entered.")
            return None

    return config


def read_payload(file_path):
    """
    Reads the actual content from the file path specified in the config.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None

    print(f"Reading data from: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


class ReliableClient:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.window_size = config["window_size"]
        self.timeout_interval = config["timeout"]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.base = 0
        self.next_seq = 0
        self.packets = []
        self.timer_start = None
        self.max_msg_size = 1024  # Will be overwritten by server

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))

            # Handshake
            print("Sending SYN...")
            self.client_socket.sendall(b"SYN")
            if self.client_socket.recv(1024).decode().strip() == "SYN/ACK":
                self.client_socket.sendall(b"ACK")
                print("Handshake Success.")
            else:
                return False

            # Negotiation
            self.client_socket.sendall(b"SIZE_REQ")
            self.max_msg_size = int(self.client_socket.recv(1024).decode())
            print(f"Max message size negotiated: {self.max_msg_size}")
            return True
        except:
            return False

    def prepare_packets(self, content):
        # We need to encode to bytes to split correctly by byte size
        content_bytes = content.encode('utf-8')
        seq = 0
        for i in range(0, len(content_bytes), self.max_msg_size):
            chunk = content_bytes[i: i + self.max_msg_size]
            # Decode back to string for JSON transport (simplifies student code)
            # In a real app we might send raw bytes, but JSON is text-based.
            packet = {
                "command": "PUSH",
                "content": chunk.decode('utf-8', errors='ignore'),
                "sequence_number": seq
            }
            self.packets.append(packet)
            seq += 1

    def run(self):
        self.client_socket.setblocking(False)
        total = len(self.packets)

        while self.base < total:
            # Send Window
            while self.next_seq < self.base + self.window_size and self.next_seq < total:
                self.send_packet(self.packets[self.next_seq])
                if self.base == self.next_seq:
                    self.timer_start = time.time()
                self.next_seq += 1

            # Receive ACKs
            try:
                data = self.client_socket.recv(1024)
                if data:
                    lines = data.decode().split('\n')
                    for line in lines:
                        if not line: continue
                        ack = json.loads(line)
                        if ack["type"] == "ACK":
                            ack_num = ack["ack_seq"]
                            print(f"Got ACK {ack_num}")
                            if ack_num >= self.base:
                                self.base = ack_num + 1
                                if self.base < self.next_seq:
                                    self.timer_start = time.time()
                                else:
                                    self.timer_start = None
            except BlockingIOError:
                pass

            # Timeout
            if self.timer_start and (time.time() - self.timer_start > self.timeout_interval):
                print("Timeout! Resending...")
                self.timer_start = time.time()
                for i in range(self.base, self.next_seq):
                    self.send_packet(self.packets[i])

        print("Done.")
        self.client_socket.close()

    def send_packet(self, pkt):
        self.client_socket.sendall((json.dumps(pkt) + "\n").encode())


if __name__ == "__main__":
    # 1. Load Params
    config = load_client_config()

    if config:
        # 2. Read the actual file content to send
        payload = read_payload(config["message_path"])

        if payload:
            client = ReliableClient("127.0.0.1", 5555, config)
            if client.connect():
                client.prepare_packets(payload)
                client.run()