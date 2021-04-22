import json

from marra_query_maker import MarraQueryMaker
from temperature_humitidy_sensor import TemperatureHumiditySensor


class Runner:
    def __init__(self):
        self.marra_database = MarraQueryMaker.getInstance()
        self.sensors = []
        self.get_temperature_and_humidity_sensors()
        self.get_readings_and_write_to_database()

    def get_temperature_and_humidity_sensors(self):
        with open('/home/pi/Projects/LocalData/sensors.json') as myFile:
            data = myFile.read()
        databases = json.loads(data)
        temperature_humidity = databases['temperature_and_humidity']
        for t in temperature_humidity:
            db_id = t['id']
            sensor_type = t['type']
            pin = t['pin']
            self.sensors.append(TemperatureHumiditySensor(db_id, sensor_type, pin))

    def get_readings_and_write_to_database(self):
        for sensor in self.sensors:
            reading = sensor.read_data()
            self.marra_database.write_current_temperature_and_humidity(reading)


if __name__ == '__main__':
    runner = Runner()


