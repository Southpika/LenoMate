import screen_brightness_control as sbc
import argparse


class operation():
    def __init__(self, brightness) -> None:
        self.brightness = brightness

    def fit(self):
        sbc.set_brightness(self.brightness)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Alter screen brightness')
    parser.add_argument('--bright', default=50)
    args = parser.parse_args()
    opt = operation(args.bright)
    opt.fit()
