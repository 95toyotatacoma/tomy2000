
import math
import time

from PIL import Image, ImageDraw
import rgb_dual_eyes as rgb
import blink_animations as blinks


WIDTH = 128
HEIGHT = 128

# Spiral appearance.
SPIRAL_STROKE = 6
SPIRAL_TURNS = 3.7
SPIRAL_RADIUS = 56

# Animation settings.
FRAME_DELAY = 0.04
LEFT_SPEED = 4.5
RIGHT_SPEED = -5.2


def draw_spiral(angle=0.0, wobble_x=0, wobble_y=0, scale=1.0):
    """
    Draw a rotating black spiral on Tomy's
    off-white eye background.
    """
    image = Image.new("RGB", (WIDTH, HEIGHT), rgb.EYE_COLOR)
    draw = ImageDraw.Draw(image)

    cx = WIDTH / 2 + wobble_x
    cy = HEIGHT / 2 + wobble_y

    points = []

    for i in range(400):
        progress = i / 399

        theta = progress * SPIRAL_TURNS * 2 * math.pi + angle
        radius = (3 + progress * SPIRAL_RADIUS) * scale

        px = cx + math.cos(theta) * radius
        py = cy + math.sin(theta) * radius

        points.append((px, py))

    draw.line(
        points,
        fill=(0, 0, 0),
        width=SPIRAL_STROKE,
        joint="curve"
    )
    # Round both ends of the spiral stroke.
    cap_radius = SPIRAL_STROKE / 2

    for px, py in (points[0], points[-1]):
        draw.ellipse(
            (
                px - cap_radius,
                py - cap_radius,
                px + cap_radius,
                py + cap_radius
            ),
            fill=(0, 0, 0)
        )

    return image


def render_dizzy(eyes, elapsed):
    """
    Render opposite-direction spirals.
    """

    left_angle = elapsed * LEFT_SPEED
    right_angle = elapsed * RIGHT_SPEED

    # Small, independent wobble.
    left_wobble_x = math.sin(elapsed * 8.0) * 2
    left_wobble_y = math.cos(elapsed * 6.0) * 2

    right_wobble_x = math.sin(elapsed * 7.3 + 1.5) * 2
    right_wobble_y = math.cos(elapsed * 8.1 + 0.8) * 2

    left_image = draw_spiral(
        left_angle,
        left_wobble_x,
        left_wobble_y
    )

    right_image = draw_spiral(
        right_angle,
        right_wobble_x,
        right_wobble_y
    )

    for index, eye in enumerate(eyes):
        if index == 0:
            output = left_image
        else:
            output = right_image.rotate(180)

        eye.show(output)


def overload_intro(eyes):
    """
    Subtle wobble, then pupils contract
    into tiny dots at the center.
    """
    print("Tomy is becoming overwhelmed...")

    # Phase 1: tiny wobble, no dramatic gaze movement.
    for i in range(12):
        t = i / 11

        wobble_x = round(math.sin(t * math.pi * 4) * 1.5)
        wobble_y = round(math.sin(t * math.pi * 3) * 1.0)

        rgb.render(
            eyes,
            x=wobble_x,
            y=wobble_y,
            pupil_radius=45
        )
        time.sleep(0.03)

    # Phase 2: pupils contract at the center.
    for i in range(12):
        t = i / 11
        smooth = t * t * (3 - 2 * t)

        radius = round(45 - 40 * smooth)

        rgb.render(
            eyes,
            x=0,
            y=0,
            pupil_radius=radius
        )
        time.sleep(0.025)

def spiral_emergence(eyes):
    """
    Grow the spirals outward from the
    contracted pupils.
    """
    print("Spirals emerging...")

    duration = 0.225
    frames = 12

    for i in range(frames + 1):
        t = i / frames

        # Smooth growth.
        smooth = t * t * (3 - 2 * t)

        scale = 0.03 + 0.97 * smooth

        left_image = draw_spiral(
            angle=0,
            scale=scale
        )

        right_image = draw_spiral(
            angle=0,
            scale=scale
        )

        for index, eye in enumerate(eyes):
            image = left_image if index == 0 else right_image.rotate(180)
            eye.show(image)

        time.sleep(duration / frames)


def dizzy_outro(eyes, final_elapsed):
    """
    Spirals slow down, shrink into their centers,
    and Tomy blinks himself back to reality.
    """
    print("Tomy is recovering...")

    # Phase 1: decelerate the spinning spirals.
    duration = 0.35
    frames = 12

    left_angle = final_elapsed * LEFT_SPEED
    right_angle = final_elapsed * RIGHT_SPEED

    for i in range(frames + 1):
        t = i / frames
        smooth = t * t * (3 - 2 * t)

        # Integrate decreasing angular velocity to stop smoothly.
        turn = t - t**3 + 0.5 * t**4

        left_image = draw_spiral(
            angle=left_angle + LEFT_SPEED * duration * turn
        )
        right_image = draw_spiral(
            angle=right_angle + RIGHT_SPEED * duration * turn
        )

        for index, eye in enumerate(eyes):
            image = left_image if index == 0 else right_image.rotate(180)
            eye.show(image)

        time.sleep(duration / frames)

    # Phase 2: shrink spirals into tiny dots.
    duration = 0.25
    frames = 12

    for i in range(frames + 1):
        t = i / frames
        smooth = t * t * (3 - 2 * t)
        scale = 1.0 - 0.97 * smooth

        left_image = draw_spiral(scale=scale)
        right_image = draw_spiral(scale=scale)

        for index, eye in enumerate(eyes):
            image = left_image if index == 0 else right_image.rotate(180)
            eye.show(image)

        time.sleep(duration / frames)

    # Phase 3: restore normal pupils.
    duration = 0.25
    frames = 10

    for i in range(frames + 1):
        t = i / frames
        smooth = t * t * (3 - 2 * t)
        radius = round(5 + 40 * smooth)

        rgb.render(
            eyes,
            x=0,
            y=0,
            pupil_radius=radius
        )

        time.sleep(duration / frames)

    # Phase 4: reuse Tomy's existing blink animation.
    blinks.recovery_blink_sequence(eyes)

    # Return to neutral.
    rgb.render(eyes, x=0, y=0)


def main():
    eyes = []

    try:
        print("Tomy is getting dizzy...")

        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        overload_intro(eyes)
        spiral_emergence(eyes)

        start = time.monotonic()

        # Normal dizzy episode: 2.5 seconds of spinning.
        spin_duration = 2.5

        while time.monotonic() - start < spin_duration:
            elapsed = time.monotonic() - start

            render_dizzy(eyes, elapsed)
            time.sleep(FRAME_DELAY)

        # Recover using the final rotation position.
        final_elapsed = time.monotonic() - start
        dizzy_outro(eyes, final_elapsed)

        print("Tomy has recovered.")

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
