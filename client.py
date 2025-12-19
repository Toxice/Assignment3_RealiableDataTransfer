import socket
import json
import time
import socket as sock
from typing import Any

# Default
IP_ADDRESS = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

def init_client():
    client_socket = sock.socket(socket.AF_INET, socket.SOCK_STREAM)

    #---- 3 Way Handshake ----
    print("Connecting to the Server, Sending [SYN]")
    client_socket.sendall(init_handshake())


def init_handshake() -> bytes:
    """
    starting the 3 Way Handshake Process
    :return: the [SYN] request in Binary Foramt
    """
    data = {"type": "SYN"}
    return msg_to_json(data)


def send_ack(client: sock.socket, segment: dict):
    ack_number = segment.get('ack')

    data = {
        "type": "ACK",
        "ack_number": ack_number
    }
    client.sendall(msg_to_json(data))

def msg_to_json(message: dict) -> bytes:
    """
    convert JSON to Bytes
    :param message: message
    :return: a Byte Array of made from the JSON dictionary
    """
    return (json.dumps(message, ensure_ascii=False) + "\n").encode(encoding='uft-8')

def to_json(msg: bytes) -> dict:
    return json.loads(msg.decode(encoding='utf-8'))


def handle_response(client: sock.socket) -> dict:
    buffer = b""
    while True:
        raw_chunk = client.recv(1024)
        if not raw_chunk:
            return {"type": "FIN"}
        buffer += raw_chunk

        if b"\n" in buffer:
            line, _, _ = buffer.partition(b"\n")
            return to_json(line)


def main():
    init_client()
