from machine import Pin
import time

# Test GPIO pins
test_pins = [2, 4, 0, 5]

for pin_number in test_pins:
    try:
        test_pin = Pin(pin_number, Pin.OUT)
        test_pin.value(1)  # Turn on
        print(f"Pin {pin_number} is valid and set to HIGH.")
        time.sleep(1)
        test_pin.value(0)  # Turn off
    except Exception as e:
        print(f"Error with pin {pin_number}: {e}")