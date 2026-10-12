import serial
import time

# Connect to Tomy's Arduino Uno
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Allow Arduino to restart after opening serial
time.sleep(2)

print("Connected to Tomy's neck controller!")

# Send command
arduino.write(b"PAN 100\n")

print("Sent command: PAN 100")

# Read Arduino responses for 2 seconds
end_time = time.monotonic() + 2

while time.monotonic() < end_time:
    if arduino.in_waiting:
        response = arduino.readline().decode(errors="replace").strip()
        print("Arduino:", response)
    else:
        time.sleep(0.05)

arduino.close()

print("Connection closed.")