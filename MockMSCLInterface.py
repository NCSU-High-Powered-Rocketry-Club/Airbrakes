class MockMSCLInterface:
    def __init__(self):
        self.iter = 0
    
    def startLoggingLoopThread(self):
        return
    
    def popDataPoint(self):
        self.iter += 1
        import time
        time.sleep(0.1)
        if (self.iter < 10):
            return {
                'accel': -9.8
            }
        else:
            return {
                'accel': 12
            }

    def stopLoggingLoop(self):
        return