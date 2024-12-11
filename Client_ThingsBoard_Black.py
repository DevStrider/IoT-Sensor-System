import time
import network
import dht
from machine import Pin
from umqtt.simple import MQTTClient

# Configuration
CONFIG = {
    "wifi_ssid": "WE6F610F",
    "wifi_pass": "0f08560c",
    "thingsboard_server": "demo.thingsboard.io",
    "token": "GeRKrLXX7xPyWU5ckA4I", #The token for the esp with the black cable
    "DHT_pin": 5,
    "read_interval": 5  # Interval in seconds
}

# Initialize DHT sensor
sensor = dht.DHT11(Pin(CONFIG["DHT_pin"]))

# Functions
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(CONFIG["wifi_ssid"], CONFIG["wifi_pass"])
        while not wlan.isconnected():
            time.sleep(1)
            print("Still connecting...")
    print("Connected to WiFi. Network Config:", wlan.ifconfig())

def send_telemetry(client, temperature, humidity):
    try:
        telemetry = {
            "temperature": temperature,
            "humidity": humidity
        }
        client.publish("v1/devices/me/telemetry", str(telemetry).replace("'", '"'))
        print("Data sent to ThingsBoard:", telemetry)
    except Exception as e:
        print("Failed to send telemetry data:", e)

def main():
    # Connect to WiFi
    connect_wifi()

    # Connect to ThingsBoard using MQTT
    client = MQTTClient("esp8266_client", CONFIG["thingsboard_server"], user=CONFIG["token"], password="")
    try:
        client.connect()
        print("Connected to ThingsBoard")
    except Exception as e:
        print("Failed to connect to ThingsBoard:", e)
        return

    # Main loop to send data
    try:
        while True:
            try:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                print(f"Temperature: {temperature}°C, Humidity: {humidity}%")

                # Send telemetry data
                send_telemetry(client, temperature, humidity)
                time.sleep(CONFIG["read_interval"])
            except Exception as e:
                print("Error in reading sensor or sending data:", e)
    except KeyboardInterrupt:
        print("Program interrupted. Disconnecting...")
        client.disconnect()

if __name__ == "__main__":
    main()

