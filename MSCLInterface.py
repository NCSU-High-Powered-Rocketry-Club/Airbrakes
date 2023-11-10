from io import TextIOWrapper
import threading
from collections import deque
from ABDataPoint import ABDataPoint
import mscl

# TOOD (Before every launch): Make sure this value is correct
UPSIDE_DOWN = True

class MSCLInterface:
    """
    The MSCL interface is used to interact with the data collected by the
    Parker-LORD 3DMCX5-AR.
    """
    def __init__ ( self, port, raw_data_logfile: TextIOWrapper, est_data_logfile: TextIOWrapper):
        # creating data node
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.raw_data_logfile = raw_data_logfile
        self.est_data_logfile = est_data_logfile

        self.databuffer = deque()

        self.running = False

        # rate in which we poll date  in miliseconds (1/(Hz)*1000)
        self.polling_rate = int(1/(100)*1000)

        self.last_time = 0


    def stop_logging_loop(self):
        """ Stops the logging loop. """
        self.running = False
        self.logging_thread.join()
        self.raw_data_logfile.close()
        self.est_data_logfile.close()


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

        have_raw = False
        have_est = False
        while self.running:
            # get all the data packets from the node with a timeout of the
            # polling rate in milliseconds
            packets: mscl.MipDataPackets = self.node.getDataPackets(self.polling_rate)

            packet: mscl.MipDataPacket
            for packet in packets:
                # Log the headers to a file if we haven't already
                if (not have_raw):
                    data_point: mscl.MipDataPoint
                    for data_point in packet.data():
                        if (data_point.channelName() [:3] != "est"):
                            self.print_headers(packet,self.raw_data_logfile)
                            have_raw = True
                        break

                if (not have_est):
                    for data_point in packet.data():
                        if (data_point.channelName() [:3] == "est"):
                            self.print_headers(packet, self.est_data_logfile)
                            have_est = True
                        break

                if (not have_est) or (not have_raw):
                    break

                # write the acceleration and time data to the data buffer
                # also write all other data to file
                self._write_data_to_file(packet)

    def print_headers(self, packet, logfile):
            for data_point in packet.data(): 
                logfile.write(str(data_point.channelName())+",")
            logfile.write("\n")


    def pop_data_point(self) -> ABDataPoint:
        """Pops a data point off of the left of the databuffer deque"""
        try:
            ret: ABDataPoint = self.databuffer.popleft()
            self.last_time = ret.timestamp
            return ret
        except IndexError:
            return None


    def _write_data_to_file(self, packet: mscl.MipDataPacket):
        data_object: ABDataPoint = {}

        data_object.timestamp = packet.collectedTimestamp().nanoseconds()

        isEst = packet.data()[0].channelName() [:3] == "est"

        logfile = self.est_data_logfile if isEst else self.raw_data_logfile

        # TODO: TEST THIS with the imu
        data_point: mscl.MipDataPoint
        for data_point in packet.data():

            # get the channel data
            match data_point.channelName():
                case "estLinearAccelX":
                    accel = data_point.as_float()
                    if UPSIDE_DOWN:
                        accel = -accel
                    data_object.accel = accel
                case "estPressureAlt":
                    data_object.altitude = data_point.as_float()

            # if the data object is not empty
            if data_object:
                # send the processed data to the databuffer
                self.databuffer.append(data_object)

            logfile.write(str(data_point.as_float())+",")
        logfile.write("\n")
