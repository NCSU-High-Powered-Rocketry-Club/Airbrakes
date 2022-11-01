# import the mscl library
import sys
import mscl

file = open("./logs/LORDlog.csv", "a")

# TODO: change these constants to match your setup
COM_PORT = "/dev/ttyACM0"
# create a Serial Connection with the specified COM Port, default baud rate of 921600
connection = mscl.Connection.Serial(COM_PORT)
# create an InertialNode with the connection
node = mscl.InertialNode(connection)

# endless loop of reading in data
n = 0
while True:
        # get all the data packets from the node, with a timeout of 500 milliseconds
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
            for dataPoint in packet.data():
                # print out the channel data
                #print(dataPoint.channelName() + ":", dataPoint.as_string())
                file.write(str(dataPoint.as_float()) + ",")
            file.write("\n")


