import time
import math
import spidev
import lgpio
import random

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

PUPIL_RADIUS = 45
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

    for index, eye in enumerate(eyes):
        if index == 1:
            # Rotate Tomy's right OLED 180 degrees
            output = image.rotate(180)
        else:
            output = image

        eye.show(output)


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

def suspicious_squint(eyes, x, y):
    """
    Slowly narrow Tomy's eyes as if he's
    examining something suspicious.
    """

    # Gradually narrow the eyelids.
    for openness in [1.0, 0.85, 0.70, 0.55, 0.42]:
        render(eyes, x, y, openness)
        time.sleep(0.09)

    # Hold the suspicious expression.
    time.sleep(1.1)

    # Slowly relax.
    for openness in [0.50, 0.65, 0.80, 1.0]:
        render(eyes, x, y, openness)
        time.sleep(0.10)

def suspicious_double_take(eyes, current):
    """
    Tomy notices something, dismisses it,
    then quickly looks back with suspicion.
    """

    # Choose a sideways direction.
    direction = random.choice([-1.0, 1.0])
    target = (direction * 0.85, -0.1)

    # Something catches his eye.
    move_gaze(eyes, current, target, 0.30)
    time.sleep(0.45)

    # Dismiss it.
    move_gaze(eyes, target, (0.0, 0.0), 0.40)
    time.sleep(0.65)

    # Wait... WHAT was that?
    move_gaze(eyes, (0.0, 0.0), target, 0.16)
    time.sleep(0.55)

    # Examine the suspicious thing.
    suspicious_squint(eyes, *target)

    # A final deliberate blink.
    blink(eyes, *target)

    # Return to normal, pretending nothing happened.
    move_gaze(eyes, target, (0.0, 0.0), 0.55)

    return (0.0, 0.0)

def main():
    eyes = []

    try:
        print("Waking Tomy's RGB eyes...")

        for config in EYES:
            eyes.append(EyeDisplay(config))

        current = (0.0, 0.0)
        render(eyes, *current)
        time.sleep(1)

        print("Tomy is curious...")

        test_duration = 60.0
        start_time = time.monotonic()
        next_blink = start_time + random.uniform(2.5, 5.0)

        positions = [
            (0.0, 0.0),
            (-0.8, 0.0),
            (0.8, 0.0),
            (0.0, -0.7),
            (0.0, 0.7),
            (-0.6, -0.4),
            (0.6, -0.4),
            (-0.6, 0.4),
            (0.6, 0.4),
        ]

        while time.monotonic() - start_time < test_duration:

            # Prefer returning to center.
            if random.random() < 0.40:
                target = (0.0, 0.0)
            else:
                target = random.choice(positions[1:])

            # Natural variation in gaze speed.
            duration = random.uniform(0.35, 0.65)

            move_gaze(eyes, current, target, duration)
            current = target

            # Hold attention for a variable duration.
            hold = random.uniform(1.0, 3.0)
            hold_end = min(
                time.monotonic() + hold,
                start_time + test_duration
            )

            # Blink independently of gaze movement.
            while time.monotonic() < hold_end:
                if time.monotonic() >= next_blink:
                    blink(eyes, *current)
                    next_blink = (
                        time.monotonic()
                        + random.uniform(3.0, 6.0)
                    )

                time.sleep(0.05)

            # Rare playful double take.
            # Occasionally Tomy notices something suspicious.
            if (
                random.random() < 0.18
                and time.monotonic() - start_time < test_duration - 5.0
            ):
                current = suspicious_double_take(eyes, current)
                previous = current

                move_gaze(eyes, current, (0.0, 0.0), 0.25)
                time.sleep(0.15)

                move_gaze(eyes, (0.0, 0.0), previous, 0.20)
                current = previous

                time.sleep(0.5)

        # Return to neutral when the test finishes.
        move_gaze(eyes, current, (0.0, 0.0), 0.5)

        print("Tomy's Curious Idle test complete!")

    finally:
        for eye in eyes:
            eye.close()

        lgpio.gpiochip_close(gpio)


if __name__ == "__main__":
    main()