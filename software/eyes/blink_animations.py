
"""Reusable eyelid gestures for TOMY's RGB eyes."""

import time

import rgb_dual_eyes as rgb


def eyelid_gesture(
    eyes,
    minimum_openness=0.0,
    closing_delay=0.035,
    opening_delay=0.045,
    hold=0.04,
    x=0,
    y=0,
):
    """Close and reopen the eyelids to a chosen depth."""

    minimum_openness = max(0.0, min(1.0, minimum_openness))

    for fraction in (0.0, 0.35, 0.75, 1.0):
        openness = 1.0 - (1.0 - minimum_openness) * fraction
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(closing_delay)

    time.sleep(hold)

    for fraction in (0.0, 0.35, 0.75, 1.0):
        openness = minimum_openness + (1.0 - minimum_openness) * fraction
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(opening_delay)


def full_blink(eyes, x=0, y=0):
    """A slightly faster, complete expressive blink."""

    # Close quickly.
    for openness in (1.0, 0.65, 0.25, 0.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.025)

    # Brief closed-eye hold.
    time.sleep(0.04)

    # Reopen smoothly.
    for openness in (0.0, 0.25, 0.65, 1.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.035)


def half_blink(eyes, x=0, y=0):
    """
    Fast, complete blink.
    Eyelids meet at the center.
    """
    for openness in (1.0, 0.4, 0.0, 0.5, 1.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.018)


def micro_blink(eyes, x=0, y=0):
    """
    Extremely fast, complete blink.
    A brief eyelid flicker.
    """
    for openness in (1.0, 0.0, 1.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.012)



def double_blink(eyes, x=0, y=0, gap=0.10):
    """Two normal full blinks."""
    full_blink(eyes, x, y)
    time.sleep(gap)
    full_blink(eyes, x, y)


def left_wink(eyes, x=0, y=0):
    """
    Close Tomy's left eye completely,
    while keeping his right eye open.
    """

    # Close left eyelid.
    for openness in (1.0, 0.65, 0.25, 0.0):
        rgb.render(
            eyes,
            x=x,
            y=y,
            left_openness=openness,
            right_openness=1.0,
        )
        time.sleep(0.035)

    # Hold the wink for a playful beat.
    time.sleep(0.18)

    # Reopen left eyelid.
    for openness in (0.0, 0.25, 0.65, 1.0):
        rgb.render(
            eyes,
            x=x,
            y=y,
            left_openness=openness,
            right_openness=1.0,
        )
        time.sleep(0.045)


def startled_blink(eyes, x=0, y=0):
    """
    Fast, complete blink.
    Tomy's startled 'WHOA!' reaction.
    """
    # Snap shut.
    for openness in (1.0, 0.35, 0.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.015)

    # Very brief closure.
    time.sleep(0.025)

    # Snap open.
    for openness in (0.0, 0.5, 1.0):
        rgb.render(eyes, x=x, y=y, openness=openness)
        time.sleep(0.020)


def recovery_blink_sequence(eyes, x=0, y=0):
    """
    WHOA! ... processing ... blink-blink!
    """
    startled_blink(eyes, x, y)

    # Tomy stares in disbelief.
    time.sleep(2.0)

    # Two rapid, fully closing blinks.
    half_blink(eyes, x, y)
    time.sleep(0.07)
    half_blink(eyes, x, y)
