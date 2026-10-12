import time
import math
import board
import adafruit_tca9548a
import adafruit_ssd1306

from PIL import Image, ImageDraw

# ==========================================
# TOMY EYE SYSTEM — V0.2
# Synchronized Gaze Control
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

# Display dimensions
WIDTH = 128
HEIGHT = 64

# Pupil settings
PUPIL_RADIUS = 20

# Center position
CENTER_X = 64
CENTER_Y = 32

# Maximum pupil movement
MAX_X = 40
MAX_Y = 12

# Current gaze position
current_x = CENTER_X
current_y = CENTER_Y


def draw_eyes(x, y):
    """Draw synchronized pupils on both displays."""

    image = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(image)

    # Dark pupil
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


def ease(t):
    """Smooth acceleration and deceleration."""
    return t * t * (3 - 2 * t)


def move_gaze(target_x, target_y, duration=0.2):
    """Move both pupils smoothly to a target position."""

    global current_x, current_y

    start_x = current_x
    start_y = current_y

    steps = 3

    for step in range(steps + 1):
        t = step / steps
        smooth_t = ease(t)

        x = start_x + (target_x - start_x) * smooth_t
        y = start_y + (target_y - start_y) * smooth_t

        draw_eyes(int(x), int(y))

        time.sleep(duration / steps)

    current_x = target_x
    current_y = target_y


# ==========================================
# GAZE POSITIONS
# ==========================================

POSITIONS = {
    "CENTER": (CENTER_X, CENTER_Y),

    "LEFT": (CENTER_X - MAX_X, CENTER_Y),
    "RIGHT": (CENTER_X + MAX_X, CENTER_Y),

    "UP": (CENTER_X, CENTER_Y - MAX_Y),
    "DOWN": (CENTER_X, CENTER_Y + MAX_Y),

    "UP_LEFT": (CENTER_X - MAX_X, CENTER_Y - MAX_Y),
    "UP_RIGHT": (CENTER_X + MAX_X, CENTER_Y - MAX_Y),

    "DOWN_LEFT": (CENTER_X - MAX_X, CENTER_Y + MAX_Y),
    "DOWN_RIGHT": (CENTER_X + MAX_X, CENTER_Y + MAX_Y),
}


# ==========================================
# MAIN PROGRAM
# ==========================================

print("TOMY EYE SYSTEM V0.2")
print("Available commands:")
print(", ".join(POSITIONS.keys()))
print("Type EXIT to quit.")

draw_eyes(current_x, current_y)

while True:
    command = input("\nGaze command: ").strip().upper()

    if command == "EXIT":
        break

    if command in POSITIONS:
        x, y = POSITIONS[command]
        move_gaze(x, y)
        print(f"Tomy is looking {command.lower()}.")

    else:
        print("Unknown command.")