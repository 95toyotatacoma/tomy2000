import time
import spidev
import lgpio

from PIL import Image, ImageDraw

# -----------------------------------
# TOMY RGB EYE — SPI5 TEST
# Waveshare 1.5" SSD1351 RGB OLED
# -----------------------------------

WIDTH = 128
HEIGHT = 128

# GPIO assignments (BCM numbering)
DC = 22
RST = 23

# Open SPI5, chip select 0
spi = spidev.SpiDev()
spi.open(5, 1)
spi.max_speed_hz = 8_000_000
spi.mode = 0

# GPIO setup
gpio = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(gpio, DC, 0)
lgpio.gpio_claim_output(gpio, RST, 1)


def command(value):
    lgpio.gpio_write(gpio, DC, 0)
    spi.writebytes([value])


def data(values):
    lgpio.gpio_write(gpio, DC, 1)
    spi.writebytes(values)


def reset():
    lgpio.gpio_write(gpio, RST, 0)
    time.sleep(0.05)
    lgpio.gpio_write(gpio, RST, 1)
    time.sleep(0.05)


def initialize():
    reset()

    command(0xFD)  # Command lock
    data([0x12])

    command(0xFD)
    data([0xB1])

    command(0xAE)  # Display off

    command(0xB3)  # Clock divider
    data([0xF1])

    command(0xCA)  # Multiplex ratio
    data([0x7F])

    command(0xA0)  # Remap / color depth
    data([0x74])

    command(0x15)  # Column address
    data([0x00, 0x7F])

    command(0x75)  # Row address
    data([0x00, 0x7F])

    command(0xA1)  # Display start line
    data([0x00])

    command(0xA2)  # Display offset
    data([0x00])

    command(0xB5)  # GPIO
    data([0x00])

    command(0xAB)  # Function selection
    data([0x01])

    command(0xB1)  # Precharge
    data([0x32])

    command(0xBE)  # VCOMH
    data([0x05])

    command(0xA6)  # Normal display

    command(0xAF)  # Display on


def show_image(image):
    # Convert RGB888 to RGB565
    pixels = []

    for r, g, b in image.getdata():
        color = (
            ((r & 0xF8) << 8)
            | ((g & 0xFC) << 3)
            | (b >> 3)
        )

        pixels.append((color >> 8) & 0xFF)
        pixels.append(color & 0xFF)

    command(0x15)
    data([0x00, 0x7F])

    command(0x75)
    data([0x00, 0x7F])

    command(0x5C)

    lgpio.gpio_write(gpio, DC, 1)

    # Send image in chunks
    for i in range(0, len(pixels), 4096):
        spi.writebytes(pixels[i:i + 4096])


try:
    print("Initializing Tomy's SPI5 RGB eye...")

    initialize()

    # Create off-white eye
    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (218, 218, 218)
    )

    draw = ImageDraw.Draw(image)

    # Black pupil
    pupil_radius = 35
    cx = WIDTH // 2
    cy = HEIGHT // 2

    draw.ellipse(
        (
            cx - pupil_radius,
            cy - pupil_radius,
            cx + pupil_radius,
            cy + pupil_radius
        ),
        fill=(0, 0, 0)
    )

    show_image(image)

    print("TOMY'S RGB EYE IS AWAKE!")

    time.sleep(10)

finally:
    spi.close()
    lgpio.gpiochip_close(gpio)