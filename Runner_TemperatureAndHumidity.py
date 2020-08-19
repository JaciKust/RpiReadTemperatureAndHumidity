#!/usr/bin/python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Common'))
import LocalDatabaseConfig
import TemperatureSensorConfig
import Adafruit_DHT
from datetime import datetime
import time
import psycopg2

if len(sys.argv) != 1:
    print("Usage: Runner_TemperatureAndHumidity.py")
    exit(1)

class EnvironmentReading:
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def __repr__(self):
        return 'Temp: {0:0.1f} F  Humidity: {1:0.1f} %'\
            .format(self.temperature, self.humidity)


num_reads = 5
readings = []

for x in range(num_reads):
    sensor_pin = TemperatureSensorConfig.temperature_sensor["pin"]
    sensor_type = TemperatureSensorConfig.temperature_sensor["type"]
    humidity_reading, temperature_reading = Adafruit_DHT.read_retry(sensor_type, sensor_pin)
    temperature_reading_f = temperature_reading * 1.8 + 32
    r = EnvironmentReading(temperature_reading_f, humidity_reading)
    print(r)
    readings.append(r)
    time.sleep(1)

database_host = LocalDatabaseConfig.postgres["host"]
database_name = LocalDatabaseConfig.postgres["dbName"]
database_user = LocalDatabaseConfig.postgres["user"]
database_pass = LocalDatabaseConfig.postgres["password"]

with psycopg2.connect(
        dbname=database_name,
        host=database_host,
        user=database_user,
        password=database_pass
) as conn:

    # There is no need for transactions here, no risk of inconsistency etc
    conn.autocommit = True

    cursor = conn.cursor()

    sql_command = """
        INSERT INTO
          environment_reading
          (temperature, humidity)
        VALUES
          (%s, %s);
    """

    for reading in readings:
        cursor.execute(sql_command, (reading.temperature, reading.humidity))

    print('[{}]: Recorded {} environment readings'.format(datetime.now(), len(readings)))

    cursor.close()
