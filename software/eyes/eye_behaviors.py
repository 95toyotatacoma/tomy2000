import time
import random
import board
import adafruit_tca9548a
import adafruit_ssd1306

from PIL import Image, ImageDraw

# ==========================================
# TOMY EYE SYSTEM — V0.4
# Autonomous Eye Behaviors
# ==========================================

# Hardware
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

left_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

right_eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[1], addr=0x3C
)

eyes = [left_eye, right_eye]

# Display
WIDTH = 128
HEIGHT = 64

# Pupil configuration
PUPIL_RADIUS = 20

CENTER_X = 64
CENTER_Y = 32

MAX_X = 40
MAX_Y = 12

# Animation
STEPS = 3
MOVE_DURATION = 0.2

current_x = CENTER_X
current_y = CENTER_Y


# ==========================================
# DRAWING
# ==========================================

def draw_eyes(x, y):

    image = Image.new("1", (WIDTH, HEIGHT), 1)
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


# ==========================================
# MOVEMENT
# ==========================================

def ease(t):
    return t * t * (3 - 2 * t)


def move_gaze(target_x, target_y, duration=MOVE_DURATION):

    global current_x, current_y

    start_x = current_x
    start_y = current_y

    for step in range(STEPS + 1):

        t = step / STEPS
        smooth_t = ease(t)

        x = start_x + (target_x - start_x) * smooth_t
        y = start_y + (target_y - start_y) * smooth_t

        draw_eyes(int(x), int(y))
        time.sleep(duration / STEPS)

    current_x = target_x
    current_y = target_y


# ==========================================
# GAZE POSITIONS
# ==========================================

POSITIONS = {
    "CENTER": (64, 32),
    "LEFT": (24, 32),
    "RIGHT": (104, 32),
    "UP": (64, 20),
    "DOWN": (64, 44),
    "UP_LEFT": (24, 20),
    "UP_RIGHT": (104, 20),
    "DOWN_LEFT": (24, 44),
    "DOWN_RIGHT": (104, 44),
}


def look(direction, duration=MOVE_DURATION):
    x, y = POSITIONS[direction]
    move_gaze(x, y, duration)


# ==========================================
# BEHAVIORS
# ==========================================

def attention():
    look("CENTER", 0.15)


def curious():
    look("UP_RIGHT")
    time.sleep(0.8)
    look("CENTER")


def thinking():
    look("UP_LEFT", 0.5)
    time.sleep(2)
    look("CENTER")


def scan():
    look("LEFT")
    time.sleep(0.4)

    look("RIGHT")
    time.sleep(0.4)

    look("CENTER")


def idle():
    """Tomy occasionally glances around."""

    directions = [
        "CENTER",
        "LEFT",
        "RIGHT",
        "UP",
        "DOWN",
        "UP_LEFT",
        "UP_RIGHT",
        "DOWN_LEFT",
        "DOWN_RIGHT",
    ]

    while True:

        # Pause before next glance
        time.sleep(random.uniform(2, 6))

        direction = random.choice(directions)

        look(direction)

        # Occasionally return to center
        if random.random() < 0.6:
            time.sleep(random.uniform(0.5, 1.5))
            look("CENTER")


# ==========================================
# MAIN
# ==========================================

print("TOMY EYE SYSTEM V0.4")
print("Autonomous behavior: IDLE")
print("Press Ctrl+C to stop.")

draw_eyes(CENTER_X, CENTER_Y)

try:
    idle()

except KeyboardInterrupt:
    print("\nTomy's autonomous eye behavior stopped.")