import rgb_dual_eyes as rgb


def main():
    eyes = []

    try:
        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        # First look toward Tomy's left.
        rgb.unimpressed_side_eye(eyes, direction=-1)

        # Then look toward Tomy's right.
        rgb.unimpressed_side_eye(eyes, direction=1)

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()