class MockMSCLInterface:
    def __init__(self):
        self.iter = 0
    
    def start_logging_loop_thread(self):
        return
    
    def pop_data_point(self):
        self.iter += 1
        import time
        time.sleep(0.001)
        if (self.iter < 100):
            return {
                'accel': 0
            }
        else:
            return {
                'accel': -8
            }

    def stop_logging_loop(self):
        return