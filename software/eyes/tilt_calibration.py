import serial
import time

# TOMY V0.8 — TILT CALIBRATION

arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

time.sleep(2)

print("\nTOMY TILT CALIBRATION")
print("---------------------")
print("Commands:")
print("  UP 5")
print("  DOWN 5")
print("  CENTER")
print("  EXIT")
print()
print("Move in small increments.")
print("Stop before mechanical contact.")

# Start from neutral
current_tilt = 90

def move_tilt(angle):
    global current_tilt

    # Temporary conservative test range.
    # These are NOT final mechanical limits.
    if not 70 <= angle <= 105:
        print("Outside temporary calibration range.")
        return

    arduino.write(f"TILT {angle}\n".encode())

    current_tilt = angle

    print(f"Tilt angle: {angle}°")


while True:

    command = input("\nCalibration: ").strip().upper()

    if command == "EXIT":
        break

    elif command == "CENTER":
        move_tilt(90)

    elif command.startswith("UP "):

        try:
            degrees = int(command.split()[1])
            if degrees != 5:
                print("Use 5-degree increments.")
                continue

            move_tilt(current_tilt + degrees)

        except ValueError:
            print("Invalid command.")

    elif command.startswith("DOWN "):

        try:
            degrees = int(command.split()[1])
            if degrees != 5:
                print("Use 5-degree increments.")
                continue

            move_tilt(current_tilt - degrees)

        except ValueError:
            print("Invalid command.")

    else:
        print("Unknown command.")

arduino.close()

print("Calibration complete.")