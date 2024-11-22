import socket
import threading

normal_temp_range = (20, 30)  # Define normal temperature range (20°C to 30°C)
normal_humidity_range = (30, 70)  # Define normal humidity range (30% to 70%)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5604
server_socket.bind(('127.0.0.1', port))  # Bind to localhost
server_socket.listen(100)  # Listen for up to 100 connections

# Dictionary to store client connections and their IDs
client_ids = {}
next_client_id = 1

def check_temperature(temperature):
    if temperature > normal_temp_range[1]:
        temp = "HIGH"
    elif temperature < normal_temp_range[0]:
        temp = "LOW"
    else:
        temp = "NORMAL"
    return temp

def check_humidity(humidity):
    if normal_humidity_range[0] <= humidity <= normal_humidity_range[1]:
        humidity = "NORMAL"
    else:
        humidity = "HIGH"
    return humidity


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
            # Parse sensor readings
            try:
                temperature, humidity = map(float, decode_message.split(","))
                print(f"Client {client_id}: Temp={temperature}°C, Humidity={humidity}%")
                # Determine if readings are normal or low or high or abnormal
                temperature = check_temperature(temperature)
                humidity = check_humidity(humidity)
                response = temperature + "," + humidity
                # Send the response back to the client
                client_connection.send(response.encode('utf-8'))
                print(f"Sent to Client {client_id}: {response}")
            except ValueError:
                print(f"Client {client_id} sent invalid data: {decode_message}")
                client_connection.send("INVALID DATA".encode('utf-8'))

        except Exception as e:
            print(f"Error with Client {client_id}: {e}")
            break

    # Cleanup on client disconnection
    print(f"Client {client_id} disconnected.")
    client_connection.close()
    if client_id in client_ids:
        del client_ids[client_id]


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