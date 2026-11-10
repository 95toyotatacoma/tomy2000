
import time
import rgb_dual_eyes as rgb


def main():
    eyes = []

    try:
        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        rgb.render(eyes)
        time.sleep(1)

        for i in range(3):
            print(f"Eye roll {i + 1}")
            rgb.exasperated_eye_roll(eyes)
            time.sleep(2)

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
