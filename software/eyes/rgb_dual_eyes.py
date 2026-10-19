import time
import math
import spidev
import lgpio

from PIL import Image, ImageDraw

# ==========================================
# TOMY RGB DUAL EYES
# Version 1.0
# Raspberry Pi 5 + SPI5 + SSD1351
# ==========================================

WIDTH = 128
HEIGHT = 128

EYE_COLOR = (218, 218, 218)  # #DADADA
PUPIL_COLOR = (0, 0, 0)

PUPIL_RADIUS = 29
GAZE_RADIUS = 18

FRAME_DELAY = 0.04

# BCM GPIO numbering
EYES = [
    {"name": "Eye 1", "cs": 0, "dc": 25, "rst": 24},
    {"name": "Eye 2", "cs": 1, "dc": 22, "rst": 23},
]

gpio = lgpio.gpiochip_open(0)


class EyeDisplay:
    def __init__(self, config):
        self.name = config["name"]
        self.dc = config["dc"]
        self.rst = config["rst"]

        self.spi = spidev.SpiDev()
        self.spi.open(5, config["cs"])
        self.spi.max_speed_hz = 8_000_000
        self.spi.mode = 0

        lgpio.gpio_claim_output(gpio, self.dc, 0)
        lgpio.gpio_claim_output(gpio, self.rst, 1)

        self.initialize()

    def command(self, value):
        lgpio.gpio_write(gpio, self.dc, 0)
        self.spi.writebytes([value])

    def data(self, values):
        lgpio.gpio_write(gpio, self.dc, 1)
        self.spi.writebytes(values)

    def initialize(self):
        lgpio.gpio_write(gpio, self.rst, 0)
        time.sleep(0.05)
        lgpio.gpio_write(gpio, self.rst, 1)
        time.sleep(0.05)

        commands = [
            (0xFD, [0x12]),
            (0xFD, [0xB1]),
            (0xAE, []),
            (0xB3, [0xF1]),
            (0xCA, [0x7F]),
            (0xA0, [0x74]),
            (0x15, [0x00, 0x7F]),
            (0x75, [0x00, 0x7F]),
            (0xA1, [0x00]),
            (0xA2, [0x00]),
            (0xB5, [0x00]),
            (0xAB, [0x01]),
            (0xB1, [0x32]),
            (0xBE, [0x05]),
            (0xA6, []),
            (0xAF, []),
        ]

        for cmd, values in commands:
            self.command(cmd)
            if values:
                self.data(values)

    def show(self, image):
        pixels = bytearray()

        for r, g, b in image.getdata():
            color = (
                ((r & 0xF8) << 8)
                | ((g & 0xFC) << 3)
                | (b >> 3)
            )

            pixels.append((color >> 8) & 0xFF)
            pixels.append(color & 0xFF)

        self.command(0x15)
        self.data([0, 127])

        self.command(0x75)
        self.data([0, 127])

        self.command(0x5C)
        lgpio.gpio_write(gpio, self.dc, 1)

        for i in range(0, len(pixels), 4096):
            self.spi.writebytes(pixels[i:i + 4096])

    def close(self):
        self.spi.close()


def draw_eye(x=0, y=0, openness=1.0):
    image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    cx = WIDTH // 2
    cy = HEIGHT // 2

    # The eye's visible opening shrinks during blinking.
    half_height = int((HEIGHT // 2) * openness)

    if half_height <= 0:
        return image

    # Off-white sclera
    draw.rectangle(
        (
            0,
            cy - half_height,
            WIDTH,
            cy + half_height
        ),
        fill=EYE_COLOR
    )

    # Pupil position
    px = cx + int(x * GAZE_RADIUS)
    py = cy + int(y * GAZE_RADIUS)

    draw.ellipse(
        (
            px - PUPIL_RADIUS,
            py - PUPIL_RADIUS,
            px + PUPIL_RADIUS,
            py + PUPIL_RADIUS
        ),
        fill=PUPIL_COLOR
    )

    # Mask anything outside the eyelid opening.

    # Upper eyelid
    upper_edge = cy - half_height - 1

    if upper_edge >= 0:
        draw.rectangle(
            (0, 0, WIDTH - 1, upper_edge),
            fill=(0, 0, 0)
        )

    # Lower eyelid
    lower_edge = cy + half_height + 1

    if lower_edge < HEIGHT:
        draw.rectangle(
            (0, lower_edge, WIDTH - 1, HEIGHT - 1),
            fill=(0, 0, 0)
        )

    return image


def render(eyes, x=0, y=0, openness=1.0):
    image = draw_eye(x, y, openness)

    for eye in eyes:
        eye.show(image)


def move_gaze(eyes, start, end, duration=0.5):
    frames = max(1, int(duration / FRAME_DELAY))

    for frame in range(frames + 1):
        t = frame / frames

        # Smoothstep easing
        t = t * t * (3 - 2 * t)

        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t

        render(eyes, x, y)
        time.sleep(FRAME_DELAY)


def blink(eyes, x=0, y=0):
    # Close quickly, reopen slightly more slowly.
    for openness in [1.0, 0.65, 0.25, 0.0]:
        render(eyes, x, y, openness)
        time.sleep(0.035)

    time.sleep(0.06)

    for openness in [0.0, 0.25, 0.65, 1.0]:
        render(eyes, x, y, openness)
        time.sleep(0.045)


def main():
    eyes = []

    try:
        print("Waking Tomy's RGB eyes...")

        for config in EYES:
            eyes.append(EyeDisplay(config))

        render(eyes)
        time.sleep(1)

        positions = [
            (0.0, 0.0),
            (-1.0, 0.0),
            (1.0, 0.0),
            (0.0, -1.0),
            (0.0, 1.0),
            (-0.7, -0.7),
            (0.7, -0.7),
            (-0.7, 0.7),
            (0.7, 0.7),
            (0.0, 0.0),
        ]

        current = positions[0]

        print("Tomy is looking around!")

        for target in positions[1:]:
            move_gaze(eyes, current, target)
            current = target

            time.sleep(0.3)
            blink(eyes, *current)

        render(eyes)
        print("Tomy's dual-eye animation complete!")

    finally:
        for eye in eyes:
            eye.close()

        lgpio.gpiochip_close(gpio)


if __name__ == "__main__":
    main()