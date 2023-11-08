from ABDataPoint import ABDataPoint

class MockMSCLInterface:
    def __init__(self):
        self.iter = 0
    
    def start_logging_loop_thread(self):
        return
    
    def pop_data_point(self) -> ABDataPoint:
        self.iter += 1
        import time
        time.sleep(0.001)
        
        res = ABDataPoint()

        if (self.iter < 100):
            res.accel = 0
        else:
            res.accel = -8

        return res

    def stop_logging_loop(self):
        return