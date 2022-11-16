class MockMSCLInterface:
    def __init__(self):
        self.iter = 0
    
    def start_logging_loop_thread(self):
        return
    
    def pop_data_point(self):
        self.iter += 1
        import time
        time.sleep(0.1)
        if (self.iter < 10):
            return {
                'accel': -9.8
            }
        else:
            return {
                'accel': -15
            }

    def stop_logging_loop(self):
        return