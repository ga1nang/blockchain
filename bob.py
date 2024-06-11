import socket
import threading
import time

#!q2w#e4r%t6y&u8i(o0p

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.connection_addresses = set()
        self.lock = threading.Lock()

    def connect(self, peer_host, peer_port):
        connection_address = (peer_host, peer_port)
        with self.lock:
            if connection_address in self.connection_addresses:
                print(f"Already connected to {peer_host}:{peer_port}")
                return

        try:
            connection = socket.create_connection(connection_address)
            with self.lock:
                self.connections.append(connection)
                self.connection_addresses.add(connection_address)
                print(f"Connected to {peer_host}:{peer_port}")
            threading.Thread(target=self.handle_client, args=(connection, connection_address)).start()
        except socket.error as e:
            print(f"Failed to connect to {peer_host}:{peer_port}. Error: {e}")

    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        print(f"Listening for connections on {self.host}:{self.port}")

        while True:
            connection, address = self.socket.accept()
            with self.lock:
                if address in self.connection_addresses:
                    print(f"Already accepted connection from {address}")
                    connection.close()
                    continue
                self.connections.append(connection)
                self.connection_addresses.add(address)
                print(f"Accepted connection from {address}")
            threading.Thread(target=self.handle_client, args=(connection, address)).start()

    def send_data(self, data):
        with self.lock:
            for connection in self.connections:
                try:
                    connection.sendall(data.encode())
                except socket.error as e:
                    print(f"Failed to send data. Error: {e}")
                    self.remove_connection(connection)

    def handle_client(self, connection, address):
        while True:
            try:
                data = connection.recv(1024)
                if not data:
                    break
                print(f"Received data from {address}: {data.decode()}")
            except socket.error:
                break

        print(f"Connection from {address} closed.")
        self.remove_connection(connection)

    def remove_connection(self, connection):
        with self.lock:
            if connection in self.connections:
                self.connection_addresses.remove(connection.getpeername())
                self.connections.remove(connection)
            connection.close()

    def start_listening(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

# Example usage:
if __name__ == "__main__":
    # Create a peer instance and start listening for incoming connections
    node = Peer("172.16.130.82", 8000)
    node.start_listening()

    # Give some time for the node to start listening
    time.sleep(2)

    # Connect to another peer (example IP address and port, change these accordingly)
    peer_host = "172.16.134.16"
    peer_port = 8000
    node.connect(peer_host, peer_port)

    # Send messages to connected peers
    while True:
        message = input("Enter message to send: ")
        node.send_data(message)
