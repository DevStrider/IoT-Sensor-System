import time
import socket
import network
import dht
from machine import Pin

# Configuration
CONFIG = {
    "wifi_ssid": "Abdulrahman",
    "wifi_pass": "3882345ABDU",
    "server_ip": "192.168.53.220",
    "server_port": 5604,
    "red_LED_pin": 2,
    "yellow_LED_pin": 4,
    "blue_LED_pin": 0,
    "DHT": 5,
    "read_interval": 5   ,
    "max_retries": 5
}

# Setup
red_LED = Pin(CONFIG["red_LED_pin"], Pin.OUT)
yellow_LED = Pin(CONFIG["yellow_LED_pin"], Pin.OUT)
blue_LED = Pin(CONFIG["blue_LED_pin"], Pin.OUT)
sensor = dht.DHT11(CONFIG["DHT"])

# Functions
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WIFI...")
        wlan.connect(CONFIG["wifi_ssid"], CONFIG["wifi_pass"])
        while not wlan.isconnected():
            time.sleep(1)
            print("Still not connected...")
    print("Connected to WIFI. Network Config:", wlan.ifconfig())

def connect_to_server():
    for attempt in range(CONFIG["max_retries"]):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((CONFIG["server_ip"], CONFIG["server_port"]))
            print("Connected to server:", CONFIG["server_ip"])
            return client_socket
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed:", e)
            time.sleep(5)
    print("Failed to connect to server.")
    return None

def send_readings(client_socket, temperature, humidity):
    try:
        message = f"{temperature},{humidity}"
        client_socket.send(message.encode())
        print("Sent to server:", message)
    except Exception as e:
        print("Error sending data:", e)

# Main function
def main():
    connect_wifi()
    client_socket = connect_to_server()
    if not client_socket:
        return

    try:
        while True:
            try:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                send_readings(client_socket, temperature, humidity)

                response = client_socket.recv(1024).decode()
                print("Server response:", response)

                status = response.split(",")
                if len(status) == 2:
                    red_LED.value(status[0] == "HIGH")
                    yellow_LED.value(status[0] == "LOW")
                    blue_LED.value(status[1] == "ABNORMAL")

                time.sleep(CONFIG["read_interval"])
            except Exception as e:
                print("Error in loop:", e)
                client_socket.close()
                client_socket = connect_to_server()
    except KeyboardInterrupt:
        print("Connection lost...")
        if client_socket:
            try:
                client_socket.send('CLOSE SOCKET'.encode('utf-8'))
            except Exception as e:
                print("Error notifying server:", e)
            finally:
                client_socket.close()

if __name__ == "__main__":
    main()

