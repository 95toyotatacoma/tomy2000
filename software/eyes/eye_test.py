import board
import adafruit_tca9548a
import adafruit_ssd1306

# Connect to the multiplexer
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

# Connect to OLED on channel 0
eye = adafruit_ssd1306.SSD1306_I2C(
    128, 64, tca[0], addr=0x3C
)

# Turn every pixel ON
from PIL import Image, ImageDraw

# Create a black canvas
image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)

# Draw Tomy's eyeball
draw.ellipse(
    (40, 8, 88, 56),
    fill=255
)

# Draw the pupil
draw.ellipse(
    (56, 24, 72, 40),
    fill=0
)

# Send the image to the OLED
eye.image(image)
eye.show()

print("Tomy's first eye is alive!")