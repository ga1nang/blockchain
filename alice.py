import socket

def get_ip_address():
    try:
        # Connect to an external server to get the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        return ip_address
    except Exception as e:
        return f"Error getting IP address: {e}"

# Get and print the IP address
ip_address = get_ip_address()
print(f"My IP address is: {ip_address}")


# import socket
# import threading
# import time

# class Peer:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.connections = []
#         self.connection_addresses = set()
        
        
#     def connect(self, peer_host, peer_port):
#         try:
#             connection = socket.create_connection((peer_host, peer_port))
#             connection_address = (peer_host, peer_port)
#             if connection_address not in self.connection_addresses:
#                 self.connections.append(connection)
#                 self.connection_addresses.add(connection_address)
#                 threading.Thread(target=self.handle_client, args=(connection, connection_address)).start()
#         except socket.error as e:
#             print(f"Failed to connect to {peer_host}: {peer_port}. Error {e}")
        
        
#     def listen(self):
#         self.socket.bind((self.host, self.port))
#         self.socket.listen(10)
#         print(f"Listening to connect to {self.host}:{self.port}")
        
#         while True:
#             connection, address = self.socket.accept()
#             if address not in self.connection_addresses:
#                 self.connections.append(connection)
#                 self.connection_addresses.add(address)
#                 print(f"Accepted connection from {address}")
#                 threading.Thread(target=self.handle_client, args=(connection, address)).start()
    
    
#     def send_data(self, data):
#         for connection in self.connections:
#             try:
#                 connection.sendall(data.encode())
#             except socket.error as e:
#                 print(f"Failed to send data. Error: {e}")
#                 self.connections.remove(connection)
#                 self.connection_addresses.remove(connection.getpeername())
    
    
#     def handle_client(self, connection, address):
#         while True:
#             try:
#                 data = connection.recv(1024)
#                 if not data:
#                     break
#                 print(f"Received data from {address}: {data.encode()}")
#             except socket.error:
#                 break
                
#         print(f"Connection from {address} closed.")
#         self.connections.remove(connection)
#         self.connection_addresses.remove(address)
#         connection.close()


#     def start_listening(self):
#         listen_thread = threading.Thread(target=self.listen)
#         listen_thread.start()

    
# if __name__ = "__main__":
#     node = Peer("0.0.0.0", 8000)
#     node.start_listening()
    
#     time.sleep(2)
    
#     peer_host = "172.16.190.58"
#     peer_port = 8000
#     node.connect(peer_host, peer_port)
    
#     while True:
#         message = input("Enter message to send:")
#         node.send_data(message)
    
    
    