import json
import socket
import os

# Default Server Configuration
HOST = "127.0.0.1"
PORT = 5555


def load_server_config():
    """
    Handles the requirement to load parameters from User Input OR a File.
    """
    config = {
        "max_msg_size": 20,
        "dynamic": False
    }

    print("--- Server Configuration ---")
    mode = input("Load from file (f) or manual input (m)? ").strip().lower()

    if mode == 'f':
        filename = input("Enter config file path (default: server_config.txt): ").strip() or "server_config.txt"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    # Clean up line
                    line = line.strip()
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip()

                        if key == "maximum_msg_size":
                            config["max_msg_size"] = int(val)
                        elif key == "dynamic message size":
                            config["dynamic"] = (val.lower() == "true")
            print("Loaded config from file.")
        else:
            print("File not found! Using defaults.")

    else:
        # Manual User Input
        try:
            size_in = input("Enter Max Message Size (bytes): ")
            config["max_msg_size"] = int(size_in)

            dyn_in = input("Enable Dynamic Message Size? (True/False): ")
            config["dynamic"] = (dyn_in.strip().lower() == "true")
        except ValueError:
            print("Invalid input. Using defaults.")

    return config


class Reliable_server:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.config = config  # Store the loaded config
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.address = None
        self.expected_seq = 0
        self.received_buffer = {}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        self.conn, self.address = self.server_socket.accept()
        print(f"Connection from {self.address}")

        if not self.handle_handshake():
            return

        self.handle_config_negotiation()
        self.receive_loop()

    def handle_handshake(self):
        data = self.conn.recv(1024).decode().strip()
        if data == "SYN":
            self.conn.sendall(b"SYN/ACK")
            data = self.conn.recv(1024).decode().strip()
            if data == "ACK":
                print("Handshake Completed.")
                return True
        return False

    def handle_config_negotiation(self):
        # Client asks for max size
        data = self.conn.recv(1024).decode().strip()
        if "SIZE_REQ" in data:
            size = self.config["max_msg_size"]
            print(f"Sending Max Size: {size}")
            # Send as string
            self.conn.sendall(str(size).encode())

    def receive_loop(self):
        while True:
            try:
                chunk = self.conn.recv(4096)
                if not chunk: break

                messages = chunk.decode().split('\n')
                for msg_str in messages:
                    if not msg_str: continue
                    try:
                        packet = json.loads(msg_str)
                    except:
                        continue

                    if packet.get("command") == "PUSH":
                        seq = packet.get("sequence_number")
                        if seq == self.expected_seq:
                            print(f"Packet {seq} received in order.")
                            self.expected_seq += 1
                            while self.expected_seq in self.received_buffer:
                                del self.received_buffer[self.expected_seq]
                                self.expected_seq += 1
                        elif seq > self.expected_seq:
                            self.received_buffer[seq] = packet.get("content")

                        # Send ACK for the highest contiguous
                        self.send_ack(self.expected_seq - 1)
            except Exception as e:
                print(e)
                break
        self.conn.close()

    def send_ack(self, ack_num):
        ack_packet = {"type": "ACK", "ack_seq": ack_num}
        self.conn.sendall((json.dumps(ack_packet) + "\n").encode())


if __name__ == "__main__":
    # Load configuration before starting server
    server_config = load_server_config()
    server = Reliable_server(HOST, PORT, server_config)
    server.start()