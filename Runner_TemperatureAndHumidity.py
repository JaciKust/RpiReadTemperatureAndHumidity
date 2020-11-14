#!/usr/bin/python
import sys
import os
from environment_reading import EnvironmentReading
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Common'))
import MarraDatabaseConfig
import LocalConfiguration
import sql_queries
import Adafruit_DHT
import time
import psycopg2
import statistics

marra_database_host = MarraDatabaseConfig.postgres['host']
marra_database_name = MarraDatabaseConfig.postgres['name']
marra_database_user = MarraDatabaseConfig.postgres['username']
marra_database_pass = MarraDatabaseConfig.postgres['password']

local_database_host = LocalConfiguration.local_database['host']
local_database_name = LocalConfiguration.local_database['name']
local_database_user = LocalConfiguration.local_database['username']
local_database_pass = LocalConfiguration.local_database['password']

pi_id = LocalConfiguration.raspberry['id']


def get_reading(sensor_pin, sensor_type):
    num_reads = 5
    readings = []

    for x in range(num_reads):
        humidity_reading, temperature_reading = Adafruit_DHT.read_retry(sensor_type, sensor_pin)
        temperature_reading_f = temperature_reading * 1.8 + 32
        r = EnvironmentReading(temperature_reading_f, humidity_reading)
        readings.append(r)
        time.sleep(1)

    temperature = statistics.median(map(lambda rx: rx.temperature, readings))
    humidity = statistics.median(map(lambda rx: rx.humidity, readings))
    return EnvironmentReading(temperature, humidity)


def get_database_result(query, arguments, expected_columns):
    with psycopg2.connect(
            dbname=marra_database_name,
            host=marra_database_host,
            user=marra_database_user,
            password=marra_database_pass
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(query, arguments)
        result = cursor.fetchall()
        return_list = []
        for val in result:
            return_list.append(dict(zip(expected_columns, val)))

        cursor.close()
        return return_list


def write_result_local():
    with psycopg2.connect(
            dbname=local_database_name,
            host=local_database_host,
            user=local_database_user,
            password=local_database_pass
    ) as local_connection:
        local_connection.autocommit = True
        cursor = local_connection.cursor()
        cursor.execute(sql_queries.local_insert_temperature_humidity_reading,
                       (reading.temperature, reading.humidity, pin, name, sensor_id))
        inserted_id = cursor.fetchone()[0]
        cursor.close()
        return inserted_id


def write_result_marra(inserted_id):
    with psycopg2.connect(
            dbname=marra_database_name,
            host=marra_database_host,
            user=marra_database_user,
            password=marra_database_pass
    ) as marra_connection:
        marra_connection.autocommit = True
        cursor = marra_connection.cursor()
        cursor.execute(sql_queries.marra_insert_temperature_humidity_reading,
                       (reading.temperature, reading.humidity, inserted_id, sensor_id))
        cursor.close()


id_loc = 'id'
pin_loc = 'pin'
name_loc = 'name'
type_loc = 'type'
expected = [id_loc, pin_loc, name_loc, type_loc]

sensors = get_database_result(sql_queries.select_sensors, (pi_id,), expected)

for sensor in sensors:
    sensor_id = sensor[id_loc]
    pin = sensor[pin_loc]
    sensor_type = sensor[type_loc]
    name = sensor[name_loc]

    reading = get_reading(int(sensor[pin_loc]), int(sensor[type_loc]))
    print("{} Median T: {}".format(name, reading.temperature))
    print("{} Median H: {}".format(name, reading.humidity))

    new_id = write_result_local()
    write_result_marra(new_id)
