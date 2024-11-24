import socket
import threading

# Define normal ranges
normal_temp_range = (20, 30)  # Normal temperature range (20°C to 30°C)
normal_humidity_range = (30, 70)  # Normal humidity range (30% to 70%)

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5604
server_socket.bind(('192.168.1.2', port))  # Bind to localhost
server_socket.listen(100)  # Listen for up to 100 connections

# Dictionary to store client connections and their IDs
client_ids = {}
next_client_id = 1

def check_temperature(temperature):
    """Check if temperature is normal, high, or low."""
    if temperature > normal_temp_range[1]:
        return "HIGH"
    elif temperature < normal_temp_range[0]:
        return "LOW"
    return "NORMAL"

def check_humidity(humidity):
    """Check if humidity is normal or high."""
    if normal_humidity_range[0] <= humidity <= normal_humidity_range[1]:
        return "NORMAL"
    return "HIGH"

def handle_client(client_connection, client_id):
    """Handle communication with a single client."""
    while True:
        try:
            # Receive message as bytes
            message = client_connection.recv(1024)
            if not message:  # Check for disconnection
                break

            # Decode the message
            decoded_message = message.decode('utf-8')

            # Check for the 'CLOSE SOCKET' command
            if decoded_message == 'CLOSE SOCKET':
                print(f"Client {client_id} disconnected.")
                break

            # Parse sensor readings
            try:
                temperature, humidity = map(float, decoded_message.split(","))
                print(f"Client {client_id}: Temp={temperature}°C, Humidity={humidity}%")

                # Determine statuses
                temperature_status = check_temperature(temperature)
                humidity_status = check_humidity(humidity)

                # Send response
                response = f"{temperature_status},{humidity_status}"
                client_connection.send(response.encode('utf-8'))
                print(f"Sent to Client {client_id}: {response}")
            except ValueError:
                # Handle invalid data
                print(f"Client {client_id} sent invalid data: {decoded_message}")
                client_connection.send("INVALID DATA".encode('utf-8'))

        except Exception as e:
            print(f"Error with Client {client_id}: {e}")
            break

    # Cleanup on disconnection
    client_connection.close()
    del client_ids[client_id]
    print(f"Cleaned up connection for Client {client_id}")

def main():
    """Main server function."""
    global next_client_id
    try:
        print(f"Server started on port {port}. Waiting for connections...")
        while True:
            # Accept a new client
            client_connection, client_address = server_socket.accept()
            client_id = next_client_id
            client_ids[client_id] = client_connection
            next_client_id += 1

            print(f"Connected to: {client_address[0]}: Client {client_id}")

            # Start a new thread for the client
            client_thread = threading.Thread(
                target=handle_client, args=(client_connection, client_id)
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        # Cleanup
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    main()
