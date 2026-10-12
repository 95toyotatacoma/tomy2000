import time
import math
import board
import adafruit_tca9548a
import adafruit_ssd1306

from PIL import Image, ImageDraw

# Initialize hardware
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

# Eye dimensions
WIDTH = 128
HEIGHT = 64

EYE_X = 64
EYE_Y = 32
EYE_RADIUS = 24
PUPIL_RADIUS = 8

def draw_eye(pupil_x, pupil_y):
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # White sclera
    draw.ellipse(
        (
            EYE_X - EYE_RADIUS,
            EYE_Y - EYE_RADIUS,
            EYE_X + EYE_RADIUS,
            EYE_Y + EYE_RADIUS
        ),
        fill=255
    )

    # Black pupil
    draw.ellipse(
        (
            pupil_x - PUPIL_RADIUS,
            pupil_y - PUPIL_RADIUS,
            pupil_x + PUPIL_RADIUS,
            pupil_y + PUPIL_RADIUS
        ),
        fill=0
    )

    eye.image(image)
    eye.show()


print("Tomy's eye animation started!")

try:
    while True:
        # Move pupil smoothly left and right
        for step in range(60):
            angle = step * (2 * math.pi / 60)

            pupil_x = EYE_X + int(12 * math.sin(angle))
            pupil_y = EYE_Y

            draw_eye(pupil_x, pupil_y)

            time.sleep(0.04)

except KeyboardInterrupt:
    print("Eye animation stopped.")