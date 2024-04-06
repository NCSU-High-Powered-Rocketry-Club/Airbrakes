from __future__ import annotations

from io import TextIOWrapper
import threading
from collections import deque
from ..data import ABDataPoint
import mscl

#from multiprocessing import Process, Pipe, Value

# TOOD (Before every launch): Make sure this value is correct
UPSIDE_DOWN = True


class MSCLInterface:
    """
    The MSCL interface is used to interact with the data collected by the
    Parker-LORD 3DMCX5-AR.
    """

    def __init__(
        self, port, raw_data_logfile: TextIOWrapper, est_data_logfile: TextIOWrapper
    ):
        # creating data node
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.raw_data_logfile = raw_data_logfile
        self.est_data_logfile = est_data_logfile

        #self.parent_pipe, self.child_pipe = Pipe()
        #self.running = Value("b", False)
        self.databuffer = deque()
        self.running = False

        # rate in which we poll date  in miliseconds (1/(Hz)*1000)
        self.polling_rate = int(1 / (100) * 1000)

        self.last_time: int = 0

    def stop_logging_loop(self):
        """Stops the logging loop."""
        self.running = False
        self.logging_thread.join()
        self.raw_data_logfile.close()
        self.est_data_logfile.close()

    def start_logging_loop_thread(self):
        """
        Using the threading package to create a logging loop on a separate
        thread.
        """
        #self.logging_thread = Process(target=self.start_logging_loop)
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
                if not have_raw:
                    data_point: mscl.MipDataPoint
                    for data_point in packet.data():
                        if data_point.channelName()[:3] != "est":
                            self.print_headers(packet, self.raw_data_logfile)
                            have_raw = True
                        break

                if not have_est:
                    for data_point in packet.data():
                        if data_point.channelName()[:3] == "est":
                            self.print_headers(packet, self.est_data_logfile)
                            have_est = True
                        break

                if (not have_est) or (not have_raw):
                    break

                # write the acceleration and time    data to the data buffer
                # also write all other data to file
                self._write_data_to_file(packet)

    def print_headers(self, packet, logfile):
        for data_point in packet.data():
            logfile.write(str(data_point.channelName()) + ",")
        logfile.write("\n")

    def pop_data_point(self) -> ABDataPoint | None:
        """Pops a data point off of the databuffer pipe"""
        """SIKE! just reads the data point"""
        try:
            # TODO: This should always return a data point with all felids filled
            ret: ABDataPoint = self.databuffer[-1]  #.popleft() #self.parent_pipe.recv()
            self.last_time = ret.timestamp
            return ret
        except IndexError:
            #print("Error popping data point!")
            return None

    def _write_data_to_file(self, packet: mscl.MipDataPacket):
        data_object: ABDataPoint = ABDataPoint(0.0, 0, 0.0, 0.0)
        # data_object.altitude = None

        data_object.timestamp = packet.collectedTimestamp().milliseconds()  #nanoseconds()

        isEst = packet.data()[0].channelName()[:3] == "est"

        logfile = self.est_data_logfile if isEst else self.raw_data_logfile

        # TODO: TEST THIS with the imu
        data_point: mscl.MipDataPoint
        contains_data = False

        for data_point in packet.data():

            # get the channel dat
            # TODO: Update the pi to 3.10 so we can use a match statement
            # TODO: Get velocity
            channel = data_point.channelName()

            if channel == "estLinearAccelX":
                accel: float = data_point.as_float()
                if UPSIDE_DOWN:
                    accel = -accel
                data_object.accel = accel
                contains_data = True

            elif channel == "estPressureAlt":
                data_object.altitude = data_point.as_float()
                contains_data = True

            # if the data object is not empty
            if contains_data:
                # send the processed data to the databuffer
                # update data buffer, !!!use buffer as read-only
                #self.child_pipe.send(data_object)
                self.databuffer.append(data_object)

                while len(self.databuffer) > 2:
                    self.databuffer.popleft()

            logfile.write(str(data_point.as_float()) + ",")
        logfile.write("\n")
