import threading
import time
import json
import socket

from client import ReliableClient
from server import Reliable_server

# --- Configuration ---
HOST = "127.0.0.1"
PORT = 5556  # Different port for testing
DROP_SEQ = 1  # We will simulate losing packet #1


class PacketDroppingServer(Reliable_server):
    """
    A 'Bad' Server that intentionally drops a specific packet sequence number
    to test if the client notices and resends it.
    """

    def __init__(self, host, port, config):
        super().__init__(host, port, config)
        self.has_dropped = False

    def receive_loop(self):
        print(f"[TEST SERVER] Ready. I will DROP packet sequence {DROP_SEQ} exactly once.")
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

                        # --- SABOTAGE LOGIC ---
                        if seq == DROP_SEQ and not self.has_dropped:
                            print(f"[TEST SERVER] *** SIMULATING PACKET LOSS: Ignored PUSH {seq} ***")
                            self.has_dropped = True
                            continue  # Skip processing and skip ACKing this packet
                        # ----------------------

                        if seq == self.expected_seq:
                            print(f"[TEST SERVER] Received PUSH {seq} (Good)")
                            self.expected_seq += 1
                            # Check buffer
                            while self.expected_seq in self.received_buffer:
                                print(f"[TEST SERVER] Recovering PUSH {self.expected_seq} from buffer")
                                del self.received_buffer[self.expected_seq]
                                self.expected_seq += 1
                        elif seq > self.expected_seq:
                            print(f"[TEST SERVER] Out of order PUSH {seq}. Buffering. (Expected {self.expected_seq})")
                            self.received_buffer[seq] = packet.get("content")

                        # Send ACK for the last contiguous packet
                        ack_num = self.expected_seq - 1
                        self.send_ack(ack_num)

            except Exception as e:
                print(e)
                break
        self.conn.close()


def run_test_server():
    # Setup server config manually to avoid input()
    conf = {"max_msg_size": 10, "dynamic": False}
    server = PacketDroppingServer(HOST, PORT, conf)
    server.start()


def run_test_client():
    # Give server a moment to start
    time.sleep(1)

    # Setup client config
    # We use a small window and short timeout for faster testing
    conf = {
        "message_path": "dummy",  # Not used in this direct call
        "window_size": 4,
        "timeout": 2  # 2 Seconds timeout
    }

    client = ReliableClient(HOST, PORT, conf)
    if client.connect():
        print("[TEST CLIENT] Connected. Sending 0, 1, 2, 3...")

        # Manually load packets to send
        # Packet 1 will be dropped by server
        client.packets = [
            {"command": "PUSH", "content": "A", "sequence_number": 0},
            {"command": "PUSH", "content": "B", "sequence_number": 1},  # Will drop
            {"command": "PUSH", "content": "C", "sequence_number": 2},
            {"command": "PUSH", "content": "D", "sequence_number": 3},
        ]

        # Run the client logic
        client.run()


if __name__ == "__main__":
    # Run Server in a separate thread
    t_server = threading.Thread(target=run_test_server, daemon=True)
    t_server.start()

    # Run Client in main thread
    run_test_client()