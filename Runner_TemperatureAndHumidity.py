#!/usr/bin/python
import sys
import os
from environment_readng import EnvironmentReading
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Common'))
import LocalDatabaseConfig
import TemperatureSensorConfig
import Adafruit_DHT
from datetime import datetime
import time
import psycopg2
import statistics


def get_temperature(environment_reading):
    return environment_reading.temperature_reading_f


def get_humidity(environment_reading):
    return environment_reading.humidity


if len(sys.argv) != 1:
    print("Usage: Runner_TemperatureAndHumidity.py")
    exit(1)

num_reads = 5
readings = []

for x in range(num_reads):
    sensor_pin = TemperatureSensorConfig.temperature_sensor["pin"]
    sensor_type = TemperatureSensorConfig.temperature_sensor["type"]
    humidity_reading, temperature_reading = Adafruit_DHT.read_retry(sensor_type, sensor_pin)
    temperature_reading_f = temperature_reading * 1.8 + 32
    r = EnvironmentReading(temperature_reading_f, humidity_reading)
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

    temperature = statistics.median(map(lambda rx: rx.temperature, readings))
    humidity = statistics.median(map(lambda rx: rx.humidity, readings))

    cursor.execute(sql_command, (temperature, humidity))

    print('[{}]: Recorded environment readings'.format(datetime.now()))
    print("Median T: {}".format(temperature))
    print("Median H: {}".format(humidity))

    cursor.close()
