from MSCLInterface import MSCLInterface
import asyncio

interface = MSCLInterface("/dev/ttyACM0", open("./logs/LORDlog.csv", "w"))

def main():
    interface.startLoggingLoopThread()
    liftOffDetected = False

    print("started logging loop")

    while True:
        try:
            dataPoint = interface.popDataPoint()
            if dataPoint is not None:
                if dataPoint['accel'] > 10 and not liftOffDetected:
                    print("LIFTOFF")
                    liftOffDetected = True
        except KeyboardInterrupt:
            break

    interface.stopLoggingLoop()

if __name__ == "__main__":
    main()