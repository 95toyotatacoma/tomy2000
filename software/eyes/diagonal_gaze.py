import time
import random
import serial
import board
import adafruit_tca9548a
import adafruit_ssd1306

from PIL import Image, ImageDraw

# ==========================================
# TOMY V0.9
# Simulated Spatial Awareness
# ==========================================

# ARDUINO CONNECTION
arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
time.sleep(2)

# OLED CONNECTIONS
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

left_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

right_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[1], addr=0x3C
)

eyes = [left_eye, right_eye]

# EYE CONFIGURATION
PUPIL_RADIUS = 20
CENTER_X = 64
CENTER_Y = 32

STEPS = 3
MOVE_DURATION = 0.08

current_x = CENTER_X
current_y = CENTER_Y

# NECK CONFIGURATION
PAN_CENTER = 90
PAN_LEFT = 120
PAN_RIGHT = 60

# TOMY V0.8 — CALIBRATED TILT

TILT_CENTER = 90

# Physical limits
TILT_MIN = 70
TILT_MAX = 100

# Safe autonomous positions
TILT_UP = 75
TILT_DOWN = 95

current_pan = PAN_CENTER
current_tilt = TILT_CENTER


# ==========================================
# EYE CONTROL
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

def send_neck(command):
    arduino.write((command + "\n").encode())
    print("Neck:", command)


def move_head(pan=None, tilt=None):
    global current_pan, current_tilt

    if pan is not None:
        pan = max(PAN_RIGHT, min(PAN_LEFT, pan))
        send_neck(f"PAN {pan}")
        current_pan = pan

    if tilt is not None:
        tilt = max(TILT_UP, min(TILT_DOWN, tilt))
        send_neck(f"TILT {tilt}")
        current_tilt = tilt

def diagonal_gaze(direction):
    """
    Coordinate Tomy's pupils, pan, and tilt.
    Eyes lead; head follows.
    """

    positions = {
        "UP_LEFT": {
            "eyes": (104, 20),
            "pan": 120,
            "tilt": 75
        },
        "UP_RIGHT": {
            "eyes": (24, 20),
            "pan": 60,
            "tilt": 75
        },
        "DOWN_LEFT": {
            "eyes": (104, 44),
            "pan": 120,
            "tilt": 95
        },
        "DOWN_RIGHT": {
            "eyes": (24, 44),
            "pan": 60,
            "tilt": 95
        }
    }

    if direction not in positions:
        print("Unknown diagonal direction.")
        return

    position = positions[direction]

    print(f"Behavior: DIAGONAL {direction}")

    # Eyes lead
    x, y = position["eyes"]
    move_eyes(x, y)

    time.sleep(0.05)

    # Pan and tilt move simultaneously
    pan = position["pan"]
    tilt = position["tilt"]

    send_neck(f"LOOK {pan} {tilt}")

    # Update our stored head position
    global current_pan, current_tilt
    current_pan = pan
    current_tilt = tilt

    # Allow neck movement to finish
    time.sleep(1.0)

    # Pupils settle toward center
    move_eyes(64, 32)


# ==========================================
# BEHAVIORS
# ==========================================

def glance():
    print("Behavior: GLANCE")

    direction = random.choice(["LEFT", "RIGHT", "UP", "DOWN"])

    positions = {
        "LEFT": (104, 32),
        "RIGHT": (24, 32),
        "UP": (64, 20),
        "DOWN": (64, 44),
    }

    x, y = positions[direction]
    move_eyes(x, y)

    time.sleep(random.uniform(0.4, 1.2))

    move_eyes(64, 32)


def observe():
    print("Behavior: OBSERVE")

    direction = random.choice(["LEFT", "RIGHT"])

    if direction == "LEFT":
        move_eyes(104, 32)
        time.sleep(0.05)
        move_head(pan=PAN_LEFT)

    else:
        move_eyes(24, 32)
        time.sleep(0.05)
        move_head(pan=PAN_RIGHT)

    # Give neck time to approach its destination.
    time.sleep(1.5)

    # Pupils settle while head remains turned.
    move_eyes(64, 32)


def explore():
    print("Behavior: EXPLORE")

    for _ in range(random.randint(2, 4)):
        x = random.choice([44, 64, 84])
        y = random.choice([24, 32, 40])

        move_eyes(x, y)
        time.sleep(random.uniform(0.4, 1.0))

    move_eyes(64, 32)


def think():
    print("Behavior: THINK")

    move_eyes(104, 20)
    time.sleep(0.05)

    move_head(tilt=TILT_UP)

    time.sleep(random.uniform(1, 2))

    move_eyes(64, 32)


def rest():
    print("Behavior: REST")

    move_eyes(64, 32)
    time.sleep(random.uniform(2, 4))


def reset():
    print("Behavior: RESET")

    move_eyes(64, 32)
    time.sleep(0.05)

    send_neck("CENTER")

    global current_pan, current_tilt
    current_pan = PAN_CENTER
    current_tilt = TILT_CENTER

    time.sleep(1.5)


# ==========================================
# AUTONOMOUS CONTROLLER
# ==========================================

def random_diagonal():
    direction = random.choice([
        "UP_LEFT",
        "UP_RIGHT",
        "DOWN_LEFT",
        "DOWN_RIGHT"
    ])

    diagonal_gaze(direction)


def autonomous_mode():

    print("\nTOMY DIAGONAL GAZE V0.9")
    print("Press Ctrl+C to stop.\n")

    behaviors = [
        glance,
        glance,
        explore,
        observe,
        observe,
        think,
        rest,
        reset,
        random_diagonal,
        random_diagonal,
    ]

    while True:
        behavior = random.choice(behaviors)
        behavior()

        time.sleep(random.uniform(1.5, 4))


# ==========================================
# MAIN
# ==========================================

try:
    draw_eyes(64, 32)

    send_neck("CENTER")
    time.sleep(1.5)

    autonomous_mode()

except KeyboardInterrupt:
    print("\nStopping Tomy's spatial awareness.")

finally:
    arduino.close()