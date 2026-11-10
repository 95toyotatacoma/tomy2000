import time
import rgb_dual_eyes as rgb


def main():
    eyes = []

    try:
        print("Testing Tomy's startled reaction...")

        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        rgb.render(eyes)
        time.sleep(1.5)

        # First surprise.
        rgb.startled_surprise(eyes)
        time.sleep(2.0)

        # Second surprise.
        rgb.startled_surprise(eyes)
        time.sleep(1.0)

        print("Startled surprise test complete!")

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
