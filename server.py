import socket
import json
import time
import socket as sock

# Default
IP_ADDRESS = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

def init_server():
    """
    initialize the TCP Server
    Accept a [SYN] and Send a [SYN,ACK]
    """
    server_socket = sock.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP_ADDRESS, PORT))
    server_socket.listen(1)
    print(f"Server listening on {IP_ADDRESS}:{PORT}")

    while True:
        connection, address = server_socket.accept()

        # 3 Way Handshake:
        #--- Step 1: Accept [SYN] and send [SYN,ACK]
        raw_data = connection.recv(BUFFER_SIZE)
        message = json.loads(raw_data.decode("utf-8"))

        # if message['type'] == "SYN":
        #     print("[SYN] Received from Client, Sending [SYN,ACK]")
        #     handle_response(server_socket, {"type": "SYN-ACK"})
        match message.get('type'):
            case "SYN":
                print("got SYN Request, Sending [SYN,ACK]")



def to_json(msg: bytes) -> dict:
    return json.loads(msg.decode(encoding='utf-8'))



def handle_response(server_socket: sock.socket, message):
    """
    :param server_socket: a TCP Socket for sending data over the network
    :param message: the message itself, JSON based
    """
    data = json.dumps(message)
    server_socket.sendall(data.encode(encoding='utf-8'))

def build_response(payload):
        print()



def main():
    init_server()


if __name__ == "__main__":
    main()