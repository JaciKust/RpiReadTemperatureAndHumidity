import statistics
import time

import adafruit_dht
import board
from environment_reading import EnvironmentReading


class TemperatureHumiditySensor:
    def __init__(self, db_id, sensor_type, pin):
        self.db_id = db_id
        self.sensor_type = sensor_type
        self.pin = pin

    def read_data(self):
        num_reads = 5
        readings = []

        board_pin = getattr(board, 'D{0}'.format(self.pin))
        if self.sensor_type == 22:
            dht = adafruit_dht.DHT22(board_pin)
        else:
            raise Exception("Could not determine sensor type")
        for x in range(num_reads):
            try:
                humidity_reading = dht.humidity
                temperature_reading = dht.temperature
                temperature_reading_f = temperature_reading * 1.8 + 32
                r = EnvironmentReading(temperature_reading_f, humidity_reading, self.db_id)
                readings.append(r)
                time.sleep(1)
            except:
                pass

        temperature = statistics.median(map(lambda rx: rx.temperature, readings))
        humidity = statistics.median(map(lambda rx: rx.humidity, readings))
        print("{} Median T: {}".format(self.db_id, temperature))
        print("{} Median H: {}".format(self.db_id, humidity))
        return EnvironmentReading(temperature, humidity, self.db_id)