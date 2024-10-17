import socket
import select
import sys

# initiate server socket with the TCP connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding the server socket with the localhost as ip and port number
port = 5604
server_socket.bind(('127.0.0.1', port)) # '127.0.0.1' is the localhost in ipv4

# make the socket listen on this port
server_socket.listen(1)

# listening forever
try:
    while True:
        client, add = server_socket.accept()  # when a connection to a client is accepted
        # Break the connection when ’ CLOSE SOCKET ’ is received
        while True:
            # receive message as bytes with a buffer size of 1024
            message = client.recv(1024)
            # decoding the bytes into characters
            decode_message = message.decode('utf-8')
            # Check if the message was 'CLOSE SOCKET' to close connection
            if decode_message == 'CLOSE SOCKET':
                client.close()
                break
            # otherwise capitalize the decoded message
            capitalized_message = decode_message.upper()
            # send the response as bytes again
            client.send(capitalized_message.encode('utf-8'))
except KeyboardInterrupt:
    print("Server is shutting down...")
finally:
    server_socket.close()
