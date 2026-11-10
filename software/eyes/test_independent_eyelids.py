from rgb_dual_eyes import (
    EYES,
    EyeDisplay,
    test_independent_eyelids,
    lgpio,
    gpio
)

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

def main():
    eyes = []

    try:
        for config in EYES:
            eyes.append(EyeDisplay(config))

        test_independent_eyelids(eyes)

    finally:
        for eye in eyes:
            eye.close()

        lgpio.gpiochip_close(gpio)


if __name__ == "__main__":
    main()