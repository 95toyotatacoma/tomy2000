
import time
import rgb_dual_eyes as rgb


def main():
    eyes = []

    try:
        print("Testing Tomy's pupil sizes...")

        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        print("Normal pupils: 45")
        rgb.render(eyes, pupil_radius=45)
        time.sleep(2)

        print("Slight contraction: 35")
        rgb.render(eyes, pupil_radius=35)
        time.sleep(2)

        print("Startled contraction: 25")
        rgb.render(eyes, pupil_radius=25)
        time.sleep(2)

        print("Returning to normal...")

        for radius in range(25, 46, 2):
            rgb.render(eyes, pupil_radius=radius)
            time.sleep(0.08)

        time.sleep(1)

        print("Pupil size test complete!")

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
