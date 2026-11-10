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




def draw_eye(
    x=0,
    y=0,
    openness=1.0,
    pupil_radius=None,
    lower_lid_raise=0
):
    image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    cx = WIDTH // 2
    cy = HEIGHT // 2

    if pupil_radius is None:
        pupil_radius = PUPIL_RADIUS

    pupil_radius = max(1, int(pupil_radius))
    lower_lid_raise = max(0, int(lower_lid_raise))

    # Normal eyelid opening.
    half_height = int((HEIGHT // 2) * openness)

    if half_height <= 0:
        return image

    # Off-white sclera.
    draw.rectangle(
        (0, cy - half_height, WIDTH, cy + half_height),
        fill=EYE_COLOR
    )

    # Pupil position.
    px = cx + int(x * GAZE_RADIUS)
    py = cy + int(y * GAZE_RADIUS)

    draw.ellipse(
        (
            px - pupil_radius,
            py - pupil_radius,
            px + pupil_radius,
            py + pupil_radius
        ),
        fill=PUPIL_COLOR
    )

    # Upper eyelid — unchanged.
    upper_edge = cy - half_height - 1

    if upper_edge >= 0:
        draw.rectangle(
            (0, 0, WIDTH - 1, upper_edge),
            fill=(0, 0, 0)
        )

    
    # Physical lower eyelid.
    # The OLED mounting orientation places this
    # edge at the top of our drawing coordinates.
    lower_edge = cy - half_height - 1 + lower_lid_raise

    if lower_edge >= 0:
        draw.rectangle(
            (0, 0, WIDTH - 1, min(HEIGHT - 1, lower_edge)),
            fill=(0, 0, 0)
        )


    return image



def render(
    eyes,
    x=0,
    y=0,
    openness=1.0,
    left_openness=None,
    right_openness=None,
    pupil_radius=None,
    left_lower_lid=0,
    right_lower_lid=0
):
    if left_openness is None:
        left_openness = openness

    if right_openness is None:
        right_openness = openness

    left_image = draw_eye(
        x, y, left_openness,
        pupil_radius=pupil_radius,
        lower_lid_raise=left_lower_lid
    )

    right_image = draw_eye(
        x, y, right_openness,
        pupil_radius=pupil_radius,
        lower_lid_raise=right_lower_lid
    )

    show_frames(eyes, (left_image, right_image))


def show_frames(eyes, frames):
    for index, (eye, output) in enumerate(zip(eyes, frames)):
        if index == 1:
            output = output.rotate(180)

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

def test_independent_eyelids(eyes):
    """
    TOMY V1.3
    Independent eyelid movement diagnostic.
    """

    print("Testing independent eyelids...")

    # Start with both eyes fully open.
    render(eyes)
    time.sleep(1.0)

    # Tomy's right eye slowly squints.
    for openness in [1.0, 0.85, 0.70, 0.55, 0.42]:
        render(
            eyes,
            left_openness=1.0,
            right_openness=openness
        )
        time.sleep(0.12)

    time.sleep(1.2)

    # Right eye reopens.
    for openness in [0.55, 0.70, 0.85, 1.0]:
        render(
            eyes,
            left_openness=1.0,
            right_openness=openness
        )
        time.sleep(0.12)

    time.sleep(0.8)

    # Tomy's left eye now squints.
    for openness in [1.0, 0.85, 0.70, 0.55, 0.42]:
        render(
            eyes,
            left_openness=openness,
            right_openness=1.0
        )
        time.sleep(0.12)

    time.sleep(1.2)

    # Left eye reopens.
    for openness in [0.55, 0.70, 0.85, 1.0]:
        render(
            eyes,
            left_openness=openness,
            right_openness=1.0
        )
        time.sleep(0.12)

    render(eyes)
    print("Independent eyelid test complete!")

def unimpressed_side_eye(eyes, direction=1):
    """
    TOMY V1.3 — Unimpressed Side-Eye

    A slow sideways glance followed by an uneven
    two-eye squint and a deliberately awkward pause.

    direction:
        -1 = Tomy's left
         1 = Tomy's right
    """

    center = (0.0, 0.0)
    target = (direction * 0.85, 0.0)

    print("Tomy is unimpressed...")

    # 1. Start completely neutral.
    render(eyes, *center)
    time.sleep(0.8)

    # 2. Slowly look sideways.
    move_gaze(eyes, center, target, 0.85)
    time.sleep(0.35)

    # 3. Gradually narrow both eyes unevenly.
    # The right eye becomes more skeptical.
    for left_open, right_open in [
        (1.00, 1.00),
        (0.90, 0.85),
        (0.80, 0.70),
        (0.72, 0.55),
        (0.65, 0.40),
    ]:
        render(
            eyes,
            *target,
            left_openness=left_open,
            right_openness=right_open
        )
        time.sleep(0.12)

    # 4. Hold the judgmental stare.
    time.sleep(2.0)

    # 5. Slowly reopen the eyelids.
    for left_open, right_open in [
        (0.72, 0.55),
        (0.80, 0.70),
        (0.90, 0.85),
        (1.00, 1.00),
    ]:
        render(
            eyes,
            *target,
            left_openness=left_open,
            right_openness=right_open
        )
        time.sleep(0.12)

    time.sleep(0.3)

    # Return to neutral, entirely unbothered.
    move_gaze(eyes, target, center, 0.75)
    time.sleep(0.5)

    print("Tomy has finished judging.")

def startled_surprise(eyes, current=(0.0, 0.0)):
    """
    TOMY V1.5b — Startled Surprise

    Sudden gaze shift, pupil contraction,
    startled freeze, and cautious recovery.
    """

    print("Tomy is startled!")

    # Pick which side caught his attention.
    direction = random.choice([-1.0, 1.0])
    target = (direction * 0.85, -0.1)

    # 1. Sudden attention shift.
    move_gaze(eyes, current, target, 0.16)

    # 2. Rapid pupil contraction.
    for radius in [40, 34, 28, 25]:
        render(eyes, *target, pupil_radius=radius)
        time.sleep(0.045)

    # 3. Freeze in surprise.
    time.sleep(0.65)

    # 4. Slowly recover.
    for radius in range(25, 46, 2):
        render(eyes, *target, pupil_radius=radius)
        time.sleep(0.09)

    # 5. A little hesitation before looking away.
    time.sleep(0.35)

    # 6. Cautiously return to neutral.
    move_gaze(eyes, target, (0.0, 0.0), 0.75)

    time.sleep(0.3)

    print("Tomy has recovered.")

    return (0.0, 0.0)


def exasperated_eye_roll(eyes):
    """
    TOMY V1.5c — Fast, asymmetric eye roll.
    Always sweeps left to right.
    """

    print("Tomy is rolling his eyes...")

    # Physical upward gaze uses positive Y.
    # Start with a quick upward-left glance.
    render(eyes, x=-0.65, y=0.85)
    time.sleep(0.06)

    # Fast sweep from left to right.
    for x in [-0.3, 0.1, 0.5, 0.85]:
        render(eyes, x=x, y=0.85)
        time.sleep(0.04)

    # Asymmetric lower eyelids.
    # Left rises higher than right.
    render(
        eyes,
        x=0.85,
        y=0.85,
        left_lower_lid=20,
        right_lower_lid=10
    )
    time.sleep(0.12)

    # Tiny twitch in the left lower eyelid.
    render(
        eyes,
        x=0.85,
        y=0.85,
        left_lower_lid=23,
        right_lower_lid=10
    )
    time.sleep(0.05)

    render(
        eyes,
        x=0.85,
        y=0.85,
        left_lower_lid=20,
        right_lower_lid=10
    )
    time.sleep(0.05)

    # Quick recovery.
    render(eyes, x=0.0, y=0.0)
    time.sleep(0.15)

    print("Tomy has expressed his opinion.")

    return (0.0, 0.0)

def select_idle_behavior(allow_dramatic=True):
    """
    TOMY V1.4 — Behavior Selector

    Temporary weighted selection system.
    Eventually replaceable by the AI Character Engine.
    """

    if not allow_dramatic:
        return "curious"

    return random.choices(
        population=[
            "curious",
            "suspicious",
            "unimpressed",
        ],
        weights=[
            75,
            17,
            8,
        ],
        k=1
    )[0]

def run_trance(eyes, current, transition, trance_requested):
    def frozen_eyes(_eye_index, pupil_scale):
        return draw_eye(*current, pupil_radius=PUPIL_RADIUS * pupil_scale)

    transition.enter(time.monotonic(), frozen_eyes)
    try:
        while trance_requested():
            now = time.monotonic()
            show_frames(eyes, [transition.render(now, index) for index in range(len(eyes))])
            time.sleep(max(0, FRAME_DELAY - (time.monotonic() - now)))
    finally:
        transition.leave()

    # Hold the first blink closed, then ease open before the quick flickers.
    render(eyes, *current, openness=0.0)
    time.sleep(0.65)
    reopen_start = time.monotonic()
    while True:
        progress = min(1.0, (time.monotonic() - reopen_start) / 1.15)
        render(eyes, *current, openness=progress**2 * (3 - 2 * progress))
        if progress == 1.0:
            break
        time.sleep(FRAME_DELAY)
    for openness in (0.27, 0.50, 0.28, 0.48, 0.29, 0.46):
        render(eyes, *current, openness=openness)
        time.sleep(0.025)
    render(eyes, *current)


def main(trance_requested=None):
    eyes = []

    try:
        if trance_requested is not None:
            from trance_animation import TranceTransition, prepare_strands

            transition = TranceTransition(prepare_strands())

        print("Waking Tomy's RGB eyes...")

        for config in EYES:
            eyes.append(EyeDisplay(config))

        current = (0.0, 0.0)
        render(eyes, *current)
        time.sleep(1.0)

        print("Tomy is awake and observing...")
        print("Press Ctrl+C to put Tomy to sleep.")

        next_blink = (
            time.monotonic()
            + random.uniform(2.5, 5.0)
        )

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

        last_behavior = "curious"

        # Continuous personality-driven idle.
        while True:

            if trance_requested is not None and trance_requested():
                run_trance(eyes, current, transition, trance_requested)
                next_blink = time.monotonic() + random.uniform(2.5, 5.0)

            # Prevent dramatic expressions back-to-back.
            allow_dramatic = last_behavior == "curious"

            behavior = select_idle_behavior(
                allow_dramatic=allow_dramatic
            )

            if behavior == "suspicious":

                print("Tomy noticed something suspicious...")

                current = suspicious_double_take(
                    eyes,
                    current
                )

                last_behavior = "suspicious"
                next_blink = (
                    time.monotonic()
                    + random.uniform(3.0, 6.0)
                )
                continue

            elif behavior == "unimpressed":

                print("Tomy is unimpressed...")

                # Choose which direction to judge.
                direction = random.choice([-1, 1])

                # Return to center before the expression.
                if current != (0.0, 0.0):
                    move_gaze(
                        eyes,
                        current,
                        (0.0, 0.0),
                        0.4
                    )
                    current = (0.0, 0.0)

                unimpressed_side_eye(
                    eyes,
                    direction=direction
                )

                current = (0.0, 0.0)

                last_behavior = "unimpressed"
                next_blink = (
                    time.monotonic()
                    + random.uniform(3.0, 6.0)
                )
                continue

            # Default behavior: Curious observation.

            if random.random() < 0.40:
                target = (0.0, 0.0)
            else:
                target = random.choice(positions[1:])

            # V1.4 — Variable gaze speed.
            gaze_style = random.random()

            if gaze_style < 0.70:
                # Calm, curious observation.
                duration = random.uniform(0.35, 0.65)

            elif gaze_style < 0.95:
                # Something suddenly caught Tomy's attention.
                duration = random.uniform(0.15, 0.28)

            else:
                # Slow, deliberate, slightly judgmental glance.
                duration = random.uniform(0.75, 1.10)

            move_gaze(
                eyes,
                current,
                target,
                duration
            )

            current = target

            # Natural pause with occasional blinking.
            hold = random.uniform(1.0, 3.0)
            hold_end = time.monotonic() + hold

            while time.monotonic() < hold_end:

                if trance_requested is not None and trance_requested():
                    break

                if time.monotonic() >= next_blink:
                    blink(eyes, *current)

                    next_blink = (
                        time.monotonic()
                        + random.uniform(3.0, 6.0)
                    )

                time.sleep(0.05)

            last_behavior = "curious"

    except KeyboardInterrupt:
        print("\nTomy is going to sleep...")

    finally:
        for eye in eyes:
            eye.close()

        lgpio.gpiochip_close(gpio)

        print("Tomy's RGB eyes shut down safely.")


if __name__ == "__main__":
    import argparse
    import os
    import signal

    parser = argparse.ArgumentParser(description="Run Tomy's RGB eyes.")
    parser.add_argument("--trance-control", action="store_true",
                        help="Enable SIGUSR1 to enter trance and SIGUSR2 to return.")
    args = parser.parse_args()

    if args.trance_control:
        requested = False

        def set_trance(signum, _frame):
            global requested
            requested = signum == signal.SIGUSR1

        signal.signal(signal.SIGUSR1, set_trance)
        signal.signal(signal.SIGUSR2, set_trance)
        print(f"Enter trance: kill -USR1 {os.getpid()}", flush=True)
        print(f"Return to normal: kill -USR2 {os.getpid()}", flush=True)
        main(lambda: requested)
    else:
        main()
