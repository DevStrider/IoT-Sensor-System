import socket
import threading

# initiate server socket with the TCP connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding the server socket with the localhost as ip and port number
port = 5604
server_socket.bind(('127.0.0.1', port))  # '127.0.0.1' is the localhost in ipv4
# make the socket listen on this port
server_socket.listen(100)

# Dictionary to store client connections and their IDs
client_ids = {}
next_client_id = 1

def thread(client_connection, client_id):
    while True:
        try:
            # receive message as bytes
            message = client_connection.recv(1024)
            # decoding the bytes into characters
            decode_message = message.decode('utf-8')
            # Check if the message was ’ CLOSE SOCKET ’ to close connection
            if decode_message == 'CLOSE SOCKET':
                client_connection.close()
                del client_ids[client_id]  # Remove client from the dictionary
                print(f"Client {client_id} disconnected.")  # Indicate disconnection
                break
            # otherwise capitalize the decoded message
            capitalized_message = decode_message.upper()
            # send the response as bytes again
            client_connection.send(capitalized_message.encode('utf-8'))
        except:
            # Handle potential connection errors
            del client_ids[client_id]
            print(f"Client {client_id} disconnected.")  # Indicate disconnection
            break

def Main():
    try:
        # Listening forever
        while True:
            # Accept a connection from a client
            client, add = server_socket.accept()
            global next_client_id
            client_id = next_client_id
            client_ids[client_id] = client  # Add client to the dictionary
            next_client_id += 1
            print('Connected to: {}: Client {}'.format(add[0], client_id))
            # Start a new thread to handle the client
            threading.Thread(target=thread, args=(client, client_id)).start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    Main()