from MSCLInterface import MSCLInterface
import asyncio

interface = MSCLInterface("/dev/ttyACM0", open("./logs/LORDlog.csv", "w"))

from enum import Enum

class State(Enum):
    STANDBY = 1
    LIFTOFF = 2

state = State.STANDBY

def process_standby_state(dataPoint):
    global state
    if dataPoint['accel'] > 10:
        print("LIFTOFF")
        state = State.LIFTOFF
        print(state)

def process_liftoff_state(dataPoint):
    # print("weee")
    return

def main():
    global state
    interface.startLoggingLoopThread()

    print("started logging loop")

    while True:
        try:
            dataPoint = interface.popDataPoint()
            if dataPoint is not None:
                if state == State.STANDBY:
                    process_standby_state(dataPoint)
                elif state == State.LIFTOFF:
                    process_liftoff_state(dataPoint)

        except KeyboardInterrupt:
            break

    interface.stopLoggingLoop()

if __name__ == "__main__":
    main()