import mscl

class MSCLInterface:
    def __init__ ( self, port, logfile ):
        self.connection = mscl.Connection.Serial(port)
        self.node = mscl.InertialNode(self.connection)
        self.logfile = logfile
        self.databuffer = []