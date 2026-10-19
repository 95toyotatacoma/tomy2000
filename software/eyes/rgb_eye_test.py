import time

import board
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import ssd1351

# --------------------------------------------------
# TOMY RGB EYE TEST — V1.0
# Waveshare 1.5" RGB OLED (SSD1351, 128x128)
# --------------------------------------------------

# TOMY RGB EYE — SPI1

import busio

# SPI1 uses GPIO21 for clock and GPIO20 for MOSI.
spi = busio.SPI(
    clock=board.D21,
    MOSI=board.D20,
)

# SPI1 CE0 is managed by the Linux SPI driver.
cs_pin = None

# Display control pins remain unchanged.
dc_pin = digitalio.DigitalInOut(board.D25)
rst_pin = digitalio.DigitalInOut(board.D24)

# Initialize display
display = ssd1351.SSD1351(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=rst_pin,
    width=128,
    height=128,
    baudrate=8000000,
)

# Create eye image
WIDTH = 128
HEIGHT = 128

SCLERA = (218, 218, 218)  # Off-white #DADADA
PUPIL = (0, 0, 0)         # Black

image = Image.new("RGB", (WIDTH, HEIGHT), SCLERA)
draw = ImageDraw.Draw(image)

# Large centered pupil
pupil_radius = 35
center_x = WIDTH // 2
center_y = HEIGHT // 2

draw.ellipse(
    (
        center_x - pupil_radius,
        center_y - pupil_radius,
        center_x + pupil_radius,
        center_y + pupil_radius,
    ),
    fill=PUPIL,
)

# Send image to OLED
display.image(image)

print("Tomy's first RGB eye is awake!")

# Keep script alive briefly
time.sleep(10)