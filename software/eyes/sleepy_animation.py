
"""TOMY V1.8 — Sleepy & Grumpy eyes."""

import time

from rgb_dual_eyes import (
    EYES,
    PUPIL_RADIUS,
    EyeDisplay,
    render,
)


FRAME_DELAY = 0.04


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def animate(
    eyes,
    duration,
    start,
    end,
):
    """Interpolate left/right openness, gaze, and pupil size."""
    frames = max(1, round(duration / FRAME_DELAY))

    for frame in range(frames + 1):
        t = smoothstep(frame / frames)
        values = [
            a + (b - a) * t
            for a, b in zip(start, end)
        ]

        left, right, x, y, pupil = values

        render(
            eyes,
            x=x,
            y=y,
            left_openness=left,
            right_openness=right,
            pupil_radius=round(pupil),
        )

        time.sleep(FRAME_DELAY)


def sleepy_sequence(eyes):
    """Tomy stubbornly fights falling asleep."""

    awake = (1.0, 1.0, 0.0, 0.0, PUPIL_RADIUS)
    droopy = (0.35, 0.43, 0.0, 0.12, 40)
    barely_awake = (0.12, 0.18, 0.0, 0.10, 38)
    startled = (1.0, 1.0, 0.0, 0.0, PUPIL_RADIUS)
    grumpy = (0.43, 0.52, 0.75, 0.0, 40)

    print("Tomy is getting sleepy...")
    animate(eyes, 2.5, awake, droopy)

    print("Tomy insists he's still awake.")
    animate(eyes, 1.8, droopy, barely_awake)
    time.sleep(1.5)

    # A tiny, unsuccessful effort to stay awake.
    animate(
        eyes, 0.20,
        barely_awake,
        (0.38, 0.43, 0.0, 0.0, 40),
    )
    animate(
        eyes, 0.85,
        (0.38, 0.43, 0.0, 0.0, 40),
        barely_awake,
    )
    time.sleep(0.6)

    print("I WASN'T SLEEPING!")
    animate(eyes, 0.12, barely_awake, startled)
    time.sleep(0.35)

    print("Tomy gives us a grumpy side-eye.")
    animate(eyes, 0.55, startled, grumpy)
    time.sleep(1.3)

    print("...and he's getting sleepy again.")
    animate(eyes, 2.0, grumpy, barely_awake)
    time.sleep(1.2)

    animate(eyes, 0.7, barely_awake, awake)


def main():
    eyes = []

    try:
        for config in EYES:
            eyes.append(EyeDisplay(config))

        render(eyes)
        time.sleep(0.8)

        sleepy_sequence(eyes)

        print("Sleepy animation finished.")

    finally:
        for eye in eyes:
            eye.close()


if __name__ == "__main__":
    main()
