from io import TextIOWrapper
import threading
from collections import deque
import mscl

class MSCLInterface:
    """
    Thie MSCL interface is used to interact with the data collected by the
    Parker-LORD 3DMCX5-AR.
    """
    def __init__ ( self, port, logfile: TextIOWrapper ):
        # creating data node
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.logfile = logfile
        self.databuffer = deque()
        self.running = False
        # rate in which we poll date  in miliseconds (1/(Hz)*1000)
        self.polling_rate = 1/(100)*1000


    def stop_logging_loop(self):
        """ Stops the logging loop. """
        self.running = False
        self.logging_thread.join()
        self.logfile.close()


    def start_logging_loop_thread(self):
        """
        Using the threading package to create a logging loop on a separate
        thread.
        """
        self.logging_thread = threading.Thread(target=self.start_logging_loop)
        self.logging_thread.start()


    def start_logging_loop(self):
        """
        Method used to run the logging loop until stopped by
        `stop_logging_loop`. All data collected by the IMU is logged to the 
        logfile. All the accelerating and time data is saved to the data
        buffer.
        """
        self.running = True
        counter = 0
        while self.running:
            # get all the data packets from the node with a timeout of the
            # polling rate in milliseconds
            packets = self.node.getDataPackets(self.polling_rate)

            # the first 10 data points are channel headers
            if counter < 10:
                for packet in packets:
                    for data_point in packet.data():
                        # write the channel names to log file
                        self.logfile.write(str(data_point.channelName()) + ",")
                    self.logfile.write("\n")
                    counter += 1
            else:
                for packet in packets:
                    # write all the data to the log file
                    # write the acceleration and time data to the data buffer
                    self._write_data_to_file(packet)


    def pop_data_point(self):
        """Pops a data point off of the left of the databuffer deque"""
        try:
            return self.databuffer.popleft()
        except IndexError:
            return None


    def _write_data_to_file(self, packet):
        # this data object is used to store accelerate and time data
        data_object = {}

        for data_point in packet.data():

            # get the channel data
            if data_point.channelName() == "estLinearAccelZ":
                data_object["accel"] = data_point.as_float()
                data_object["timestamp"] = packet.collectedTimestamp().nanoseconds()

            # if the data object is not empty
            if data_object:
                # send the accelerating and time data to the databuffer
                self.databuffer.append(data_object)

            self.logfile.write(str(data_point.as_float())+",")
        self.logfile.write("\n")
