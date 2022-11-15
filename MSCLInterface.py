import mscl
import asyncio
import collections.deque

class MSCLInterface:
    def __init__ ( self, port, logfile ):
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.logfile = logfile
        self.databuffer = deque()

        self.running = False

    def stopLoggingLoop():
        self.running = False

    async def startLoggingLoop():
        self.running = True
        while self.running:
            # get all the data packets from the node, with a timeout of 10 (or whatever is below) milliseconds
            packets = node.getDataPackets(50)
            if n<10:
                for packet in packets:
                    # iterate over all the data points in the packet
                    for dataPoint in packet.data():
                        # print out the channel data
                        # Note: The as_string() function is being used here for simplicity.
                        #      Other methods (ie. as_float, as_uint16, as_Vector) are also available.
                        #      To determine the format that a dataPoint is stored in, use dataPoint.storedAs().
                        print(dataPoint.channelName())
                        file.write(str(dataPoint.channelName()) + ",")
                    file.write("\n")
                    n += 1
            else:
                for packet in packets:
                    # iterate over all the data points in the packet
                    dataObject = {}
                    for dataPoint in packet.data():
                        # print out the channel data
                        #print(dataPoint.channelName() + ":", dataPoint.as_string())
                        if dataPoint.channelName() == "estPressureAlt":
                            dataObject["altitude"] = dataPoint.as_float()
                            dataObject["timestamp"] = packet.collectedTimestamp().nanoseconds()
                        if dataObject != {}:
                            dataBuffer.append(dataObject)

                        file.write(str(dataPoint.as_float())+",")
                    file.write("\n")

    def popDataPoint():
        try:
            return self.databuffer.popLeft()
        except IndexError():
            return None