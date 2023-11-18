import argparse

from AirbrakeSystem import Airbrakes

msg = "Main program that controls the flight of the rocket through airbrake systems"

parser = argparse.ArgumentParser(description=msg)

parser.add_argument("-s", "--mock_servo", action="store_true",
                    help="Use mock servo")
parser.add_argument("-i", "--mock_imu", action="store_true",
                    help="Use mock IMU")
# What is this?
# parser.add_argument("-f", "--full_deployment", default=False,
#                     action="store_true", help="Perform Full Deployent")

args = parser.parse_args()


# Uses input arguments to choose between mock and real hardware
# e.g. run as python main.py -si to run using mock servo and mock imu
# or just run python main.py to run with all real hardware

def main(args):
    airbrakes = Airbrakes(args.mock_servo, args.mock_imu)

    while not airbrakes.ready_to_shutdown:
        try:
            airbrakes.update()
        except KeyboardInterrupt:
            break

    airbrakes.shutdown()


if __name__ == "__main__":
    main(args)
