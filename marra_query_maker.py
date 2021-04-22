import json
import logging

import psycopg2

import sql_queries


class MarraQueryMaker:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MarraQueryMaker.__instance is None:
            MarraQueryMaker()
        return MarraQueryMaker.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MarraQueryMaker.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            with open('/home/pi/Projects/Data/databases.json') as myFile:
                data = myFile.read()
            databases = json.loads(data)
            marra = databases["marra"]

            self.marra_database_host = marra['host']
            self.marra_database_name = marra['name']
            self.marra_database_user = marra['username']
            self.marra_database_pass = marra['password']
            self.connection = None

            MarraQueryMaker.__instance = self

    def __del__(self):
        self.close_connection()

    def open_connection(self):
        if self.connection is not None:
            return
        try:
            self.connection = psycopg2.connect(
                dbname=self.marra_database_name,
                host=self.marra_database_host,
                user=self.marra_database_user,
                password=self.marra_database_pass
            )
            self.connection.autocommit = True
        except Exception as e:
            logging.warning("Could not connect to Marra.")
            self.close_connection()

    def close_connection(self):
        try:
            if self.connection is not None:
                self.connection.close()
        except:
            pass
        finally:
            self.connection = None

    def write_current_temperature_and_humidity(self, environment_reading):
        if self.connection is None:
            self.open_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_queries.marra_insert_temperature_humidity_reading,
                           (environment_reading.temperature, environment_reading.humidity, environment_reading.sensor_id))
            cursor.close()

        except Exception as e:
            logging.warning("Could not write temperature / humidity reading to Marra")
