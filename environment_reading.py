class EnvironmentReading:
    def __init__(self, temperature, humidity, sensor_id):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.humidity = humidity

    def __repr__(self):
        return 'Temp: {0:0.1f} F  Humidity: {1:0.1f} %'\
            .format(self.temperature, self.humidity)
