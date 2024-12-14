# Python program to implement server side of chat room .
import socket
import select
import sys

# initiate Client socket with the TCP connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding the client socket with the localhost as ip and port number
port = 5604
#try to connect to the server with associated port and id
client_socket.connect( ('127.0.0.1', port))

# open a connection until sending CLOSE SOCKET
try:
    while True:
        message = input("Enter your message: ")
        # send message as bytes
        client_socket.send(message.encode('utf-8'))
        try:
            # receive response if exists with a timeout of 1 second
            client_socket.settimeout(1)
            responses = client_socket.recv(1024)
            decode_responses = responses.decode('utf-8')
            print("Server response: " + decode_responses)
        except socket.timeout:
            print("No response received from the server.")
        if message.upper() == 'CLOSE SOCKET':
            print("Connection lost..")
            client_socket.close()
            break
except KeyboardInterrupt:
    print("Connection lost...")
    client_socket.send('CLOSE SOCKET'.encode('utf-8'))  # Notify the server
    client_socket.close()
