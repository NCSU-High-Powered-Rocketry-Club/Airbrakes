from io import TextIOWrapper
import mscl
import threading
from collections import deque

class MSCLInterface:
    def __init__ ( self, port, logfile: TextIOWrapper ):
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.logfile = logfile
        self.databuffer = deque()

        self.running = False

    def stopLoggingLoop(self):
        self.running = False
        self.loggingThread.join()
        self.logfile.close()

    def startLoggingLoopThread(self):
        self.loggingThread = threading.Thread(target=self.startLoggingLoop)
        self.loggingThread.start()

    def startLoggingLoop(self):
        self.running = True
        n = 0
        while self.running:
            # get all the data packets from the node, with a timeout of 10 (or whatever is below) milliseconds
            packets = self.node.getDataPackets(50)
            # get the channel headers
            if n<10:
                for packet in packets:
                    for dataPoint in packet.data():
                        self.logfile.write(str(dataPoint.channelName()) + ",")
                    self.logfile.write("\n")
                    n += 1
            else:
                for packet in packets:
                    # iterate over all the data points in the packet
                    dataObject = {}
                    for dataPoint in packet.data():
                        # get the channel data
                        if dataPoint.channelName() == "estLinearAccelZ":
                            dataObject["accel"] = dataPoint.as_float()
                            dataObject["timestamp"] = packet.collectedTimestamp().nanoseconds()
                            
                        if dataObject != {}:
                            self.databuffer.append(dataObject)

                        self.logfile.write(str(dataPoint.as_float())+",")
                    self.logfile.write("\n")

    def popDataPoint(self):
        try:
            return self.databuffer.popleft()
        except IndexError as e:
            return None