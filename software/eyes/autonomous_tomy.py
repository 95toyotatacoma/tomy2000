import time
import random
import serial
import board
import adafruit_tca9548a
import adafruit_ssd1306

from PIL import Image, ImageDraw

# ==========================================
# TOMY V0.6
# Autonomous Eye & Neck Behaviors
# ==========================================

# Arduino
arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
time.sleep(2)

# OLEDs
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

left_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

right_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[1], addr=0x3C
)

eyes = [left_eye, right_eye]

# Eye settings
PUPIL_RADIUS = 20
CENTER_X = 64
CENTER_Y = 32

STEPS = 3
MOVE_DURATION = 0.08

current_x = CENTER_X
current_y = CENTER_Y

# Neck positions
NECK_CENTER = 90
NECK_LEFT = 120
NECK_RIGHT = 60


# ==========================================
# EYE DRAWING
# ==========================================

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


def move_eyes(target_x, target_y, duration=MOVE_DURATION):
    global current_x, current_y

    start_x = current_x
    start_y = current_y

    for step in range(1, STEPS + 1):
        t = step / STEPS
        smooth = t * t * (3 - 2 * t)

        x = start_x + (target_x - start_x) * smooth
        y = start_y + (target_y - start_y) * smooth

        draw_eyes(int(x), int(y))
        time.sleep(duration / STEPS)

    current_x = target_x
    current_y = target_y


# ==========================================
# NECK CONTROL
# ==========================================

def neck(command):
    arduino.write((command + "\n").encode())
    print("Neck:", command)


# ==========================================
# BEHAVIORS
# ==========================================

def casual_glance():
    direction = random.choice(["LEFT", "RIGHT"])

    print("Behavior: Casual glance", direction)

    if direction == "LEFT":
        move_eyes(104, 32)
    else:
        move_eyes(24, 32)

    time.sleep(random.uniform(0.5, 1.5))
    move_eyes(64, 32)


def curious_observation():
    direction = random.choice(["LEFT", "RIGHT"])

    print("Behavior: Curious observation", direction)

    if direction == "LEFT":
        move_eyes(104, 32)
        time.sleep(0.05)
        neck(f"PAN {NECK_LEFT}")
    else:
        move_eyes(24, 32)
        time.sleep(0.05)
        neck(f"PAN {NECK_RIGHT}")

    # Give the neck time to finish moving
    time.sleep(1.5)

    # Eyes settle toward center
    move_eyes(64, 32)

    # Hold observation
    time.sleep(random.uniform(1, 3))

    # Return head to center
    neck(f"PAN {NECK_CENTER}")


def thinking():
    print("Behavior: Thinking")

    # Based on Tomy's reversed horizontal eye orientation
    move_eyes(104, 20)

    time.sleep(random.uniform(1, 2))

    move_eyes(64, 32)


def attention():
    print("Behavior: Attention")

    move_eyes(64, 32)
    time.sleep(0.05)
    neck("CENTER")


def resting():
    print("Behavior: Resting")

    move_eyes(64, 32)
    time.sleep(random.uniform(2, 5))


# ==========================================
# AUTONOMOUS CONTROLLER
# ==========================================

def autonomous_mode():
    print("\nTOMY AUTONOMOUS MODE ACTIVE")
    print("Press Ctrl+C to stop.\n")

    behaviors = [
    casual_glance,
    casual_glance,
    thinking,
    resting,
    curious_observation,
    curious_observation,
    ]

    while True:
        behavior = random.choice(behaviors)
        behavior()

        time.sleep(random.uniform(2, 5))


# ==========================================
# MAIN
# ==========================================

try:
    draw_eyes(CENTER_X, CENTER_Y)
    neck("CENTER")
    time.sleep(1)

    autonomous_mode()

except KeyboardInterrupt:
    print("\nStopping Tomy's autonomous behavior.")

finally:
    arduino.close()