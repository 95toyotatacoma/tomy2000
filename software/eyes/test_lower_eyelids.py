
import time
import rgb_dual_eyes as rgb


def main():
    eyes = []

    try:
        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        print("Normal eyelids")
        rgb.render(eyes)
        time.sleep(1.5)

        print("Testing left lower lid only")
        rgb.render(
            eyes,
            left_lower_lid=25,
            right_lower_lid=0
        )
        time.sleep(3)

        print("Testing right lower lid only")
        rgb.render(
            eyes,
            left_lower_lid=0,
            right_lower_lid=25
        )
        time.sleep(3)

        rgb.render(eyes)
        time.sleep(1)

        print("Raising asymmetric lower eyelids")

        for step in range(21):
            rgb.render(
                eyes,
                x=0,
                y=0.85,
                left_lower_lid=step,
                right_lower_lid=int(step * 0.5)
            )
            time.sleep(0.05)

        print("Holding asymmetry")
        time.sleep(1.5)

        print("Left lower eyelid twitch")

        for left_height in [22, 19, 23, 20]:
            rgb.render(
                eyes,
                x=0,
                y=0.85,
                left_lower_lid=left_height,
                right_lower_lid=10
            )
            time.sleep(0.09)

        time.sleep(1.0)

        print("Relaxing")

        for step in range(20, -1, -1):
            rgb.render(
                eyes,
                x=0,
                y=-0.85,
                left_lower_lid=step,
                right_lower_lid=int(step * 0.5)
            )
            time.sleep(0.05)

        rgb.render(eyes)
        time.sleep(1.0)

    finally:
        for eye in eyes:
            eye.close()

        rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
