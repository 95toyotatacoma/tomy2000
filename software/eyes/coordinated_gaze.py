import time
import serial
import board
import adafruit_tca9548a
import adafruit_ssd1306
from PIL import Image, ImageDraw

# ==========================================
# TOMY — COORDINATED GAZE V0.5
# ==========================================

# Arduino neck controller
arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
time.sleep(2)

# Eye hardware
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

left_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

right_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[1], addr=0x3C
)

eyes = [left_eye, right_eye]

# Eye configuration
PUPIL_RADIUS = 20
CENTER_X = 64
CENTER_Y = 32
STEPS = 3

current_x = CENTER_X
current_y = CENTER_Y


def draw_eyes(x, y):
    image = Image.new("1", (128, 64), 1)
    draw = ImageDraw.Draw(image)

    draw.ellipse(
        (
            x - PUPIL_RADIUS,
            y - PUPIL_RADIUS,
            x + PUPIL_RADIUS,
            y + PUPIL_RADIUS
        ),
        fill=0
    )

    for eye in eyes:
        eye.image(image)
        eye.show()


def move_eyes(target_x, target_y, duration=0.08):
    global current_x, current_y

    start_x = current_x
    start_y = current_y

    for step in range(1, STEPS + 1):
        t = step / STEPS
        smooth_t = t * t * (3 - 2 * t)

        x = start_x + (target_x - start_x) * smooth_t
        y = start_y + (target_y - start_y) * smooth_t

        draw_eyes(int(x), int(y))
        time.sleep(duration / STEPS)

    current_x = target_x
    current_y = target_y


def neck(command):
    arduino.write((command + "\n").encode())
    print("Neck:", command)


def look_left():
    print("Tomy looks LEFT")
    move_eyes(104, 32)
    time.sleep(0.05)
    neck("PAN 120")

def look_right():
    print("Tomy looks RIGHT")
    move_eyes(24, 32)
    time.sleep(0.05)
    neck("PAN 60")


def look_center():
    print("Tomy looks CENTER")
    move_eyes(64, 32)
    time.sleep(0.15)
    neck("CENTER")


# ==========================================
# MAIN
# ==========================================

try:
    draw_eyes(current_x, current_y)

    print("\nTOMY COORDINATED GAZE V0.5")
    print("Commands: LEFT, RIGHT, CENTER, EXIT")

    while True:
        command = input("\nCommand: ").strip().upper()

        if command == "LEFT":
            look_left()

        elif command == "RIGHT":
            look_right()

        elif command == "CENTER":
            look_center()

        elif command == "EXIT":
            break

        else:
            print("Unknown command.")

except KeyboardInterrupt:
    print("\nStopping.")

finally:
    arduino.close()