from __future__ import annotations
import argparse
from datetime import datetime
import json
import logging.config
from pathlib import Path
import sys


sys.path.append("/usr/share/python3-mscl")

from AirbrakeSystem import Airbrakes

# Uses input arguments to choose between mock and real hardware
# e.g. run as python main.py -si to run using mock servo and mock imu
# or just run python main.py to run with all real hardware
parser = argparse.ArgumentParser(
    description="Main program that controls the flight of the rocket through airbrake systems"
)

parser.add_argument("-s", "--mock_servo", action="store_true", help="Use mock servo")
parser.add_argument("-i", "--mock_imu", action="store_true", help="Use mock IMU")
parser.add_argument("-v", "--velocity", type=float, help="Vel to deploy airbrakes at")
parser.add_argument("-e", "--extension", type=float, help="Extension of airbrakes")

args = parser.parse_args()


class CSVFormatter(logging.Formatter):
    airbrakes: Airbrakes

    def format(self, record: logging.LogRecord) -> str:
        # Format as `unix millis,message`
        # support string interpolation for the message
        return f"{self.airbrakes.interface.last_time},{record.getMessage()}"


class AirbrakesDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name == "airbrakes_data"


def setup_logging():
    # Set up logging
    with open("logging_config.json", "r") as f:
        logging_config = json.load(f)

    # Make sure logs dir exists
    Path("./logs").mkdir(parents=True, exist_ok=True)

    if args.velocity is not None and args.extension is not None:
        Path("./logs/lookup_table_logs").mkdir(parents=True, exist_ok=True)
        log_file_path = logging_config["handlers"]["file"].get("filename")
        log_file_path = log_file_path.replace(
            "{filename}", f"lookup_table_logs/vel{args.velocity}ext{args.extension}"
        )
    else:
        # Set up file handler with ISO 8601 datetime in filename
        log_file_path = logging_config["handlers"]["file"].get("filename")
        log_file_path = log_file_path.replace(
            "{filename}", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )

    logging_config["handlers"]["file"]["filename"] = log_file_path

    logging.config.dictConfig(config=logging_config)


def main(args):
    setup_logging()

    if args.mock_servo and args.mock_imu:
        airbrakes = Airbrakes(True, True, args.velocity, args.extension)
    else:
        airbrakes = Airbrakes(args.mock_servo, args.mock_imu)

    # inject the airbrakes object into the CSVFormatter
    # so that we can have accurate time in sim
    logging.getHandlerByName("file").formatter.airbrakes = airbrakes

    while not airbrakes.ready_to_shutdown:
        try:
            airbrakes.update()
        except KeyboardInterrupt:
            break

    airbrakes.shutdown()


if __name__ == "__main__":
    main(args)
