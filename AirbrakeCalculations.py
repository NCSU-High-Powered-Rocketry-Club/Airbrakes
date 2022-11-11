class AirbrakeCalculations:

    # this method runs our entire code
    def airbrake_code(self):

        last_upload_time = time.time()  # initilized upload time

        print('Entering Sensor Loop, press Ctrl+C to abort.')
        print('Data Log Started\n')

        # creating the header for the CSV file
        with open('sensor_data.csv', 'a', newline='') as csv_file:

            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()

        # a for loop that will not stop throughout the entire flight
        while True:
            if self.sensor.has_data():
                self._get_sensor_data()
                self._deployment_calculations()

            current_time = time.time()
            # every logging interval, the data list will be exported to CSV
            if current_time-last_upload_time > self.logging_interval:
                self._export_to_csv()
                # clears out current data
                self.sensor_dict = {}
                self.sensor_list = []
                last_upload_time = current_time

    def _get_sensor_data(self):  # -> list[dict]:
        # get_data returns a list of dictionaries. Each dictionary has an id
        # that details what type of data is contained in that dictionary
        # {id: str, timestamp: float, data: ndarray}
        data_list = self.sensor.get_data()

        for data in data_list:
            time_stamp = data['timestamp']
            # if there is no data for the current ts, a new dict is created
            if time_stamp not in self.sensor_dict:
                self.sensor_dict[time_stamp] = dict(
                    time=None, acceleration=None, magnetometer=None,
                    gyroscope=None, euler_angle=None, quaternion=None,
                    linear_acceleration=None, gravity=None,
                    bno_temperature=None, bmp_temperature=None,
                    pressure=None, altitude=None)
                self.sensor_dict[time_stamp]['time'] = time_stamp
            # data is added to the current ts dict
            self.sensor_dict[time_stamp][data['id']] = data['data']
        # converts dict of dicts into a list of dicts

        self.sensor_data = [data for data in self.sensor_dict.values()]

    def _deployment_calculations(self):
        # not sure if we are using this on this flight
        # recent_data = list(self.sensor_data[-1].values())[-1]
        # if recent_data['altitude'] is not None:
        #     altitude = recent_data['altitude']
            # maybe also calulcate velocity here using change in altitude
            # and change in time
        pass

    def _export_to_csv(self):
        # opens the csv file to append to the end of
        with open('sensor_data.csv', 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            # writing the sensor data from the sensor_data_list to the csv
            for row in self.sensor_data:
                writer.writerow(row)