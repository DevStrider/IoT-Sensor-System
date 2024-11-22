import time
import socket
import network
import dht
from machine import Pin

wifi_ssid = "<WIFI_SSID>"
wifi_pass = "<WIFI_PASS>"
server_ip = "<SERVER_IP>"
server_port = "<SERVER_PORT>"
read_interval = 20
red_LED_pin = 2 # Temperature too high
yellow_LED_pin = 4  # Temperature too low
blue_LED_pin = 0 # Abnormal Humidity
DHT_Pin = 5

red_LED = Pin(red_LED_pin, Pin.OUT)
yellow_LED = Pin(yellow_LED_pin, Pin.OUT)
blue_LED = Pin(blue_LED_pin, Pin.OUT)
sensor = dht.DHT22(DHT_Pin)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.connected():
        print("Connecting to WIFI...")
        wlan.connect(wifi_ssid, wifi_pass)
        while not wlan.connected():
            time.sleep(1)
    print("Network Config:", wlan.ifconfig())

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print("Connected to server:", server_ip)
    return client_socket

def send_readings(client_socket, temperature, humidity):
    try:
        message = f"{temperature},{humidity}"
        client_socket.send(message.encode())
        print("Sent to server:", message)
    except Exception as e:
        print("Error sending data:", e)
        client_socket.close()
        return None
def main():
    connect_wifi()
    client_socket = connect_to_server()
    try:
        while True:
            try:
                sensor.measure()
                temperature = sensor.temperature
                humidity = sensor.humidity
                print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                send_readings(client_socket, temperature, humidity)
                response = client_socket.recv(1024).decode()
                print("Server response:", response)
                temperature_status , humidity_status = response.split(",")
                if temperature_status == "NORMAL":
                    red_LED.value(1)
                    yellow_LED.value(0)
                elif temperature_status == "LOW":
                    red_LED.value(0)
                    yellow_LED.value(1)
                elif temperature_status == "HIGH":
                    red_LED.value(1)
                    yellow_LED.value(0)

                if humidity_status == "ABNORMAL":
                    blue_LED.value(1)
                else:
                    blue_LED.value(0)
                time.sleep(read_interval)
            except Exception as e:
                print("Error:", e)
                client_socket.close()
                client_socket = connect_to_server()  # Reconnect to server if needed
    except KeyboardInterrupt:
        print("Connection lost...")
        client_socket.send('CLOSE SOCKET'.encode('utf-8'))  # Notify the server
        client_socket.close()
if __name__ == "__main__":
    main()