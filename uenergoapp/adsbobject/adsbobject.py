# -*- coding: utf-8 -*-

# from pprint import pprint

import functools
import os
import time
from datetime import datetime, timedelta
from configparser import ConfigParser
import logging
import mysql.connector
from mysql.connector import errors
import requests
from requests import exceptions

# Read credentials from *.cfg file
config = ConfigParser()
# config.read('adsbdb.cfg')
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adsbdb.cfg'))
# Pack credentials to the dictionary
credentials = dict(config['MARIADB'])
url = dict(config['OPENSKY'])['url']

# Enable logging
logfile = 'adsbdb.log'
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')


def timer_logger(function):
    """
    Calculates and log the execution time of any function or method .

    :param function: Any function or method
    :return: Decorated function or method
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Get start time
        value = function(*args, **kwargs)  # Execute the function
        stop = time.perf_counter()  # Get stop time
        # Log the function name and and execution time
        logging.info(f'EXECUTE the function {function.__name__} in {stop - start} sec.')

        return value

    return wrapper


class MySQLCursorContextManager:
    """
    Context manager for mysql.connector.connection.cursor.
    Closes the cursor on the exit from the runtime context.

    Attributes:
        mysql_connector_connection (object): mysql.connector.connection_cext.CMySQLConnection object OR other
        database.connector.connection object where the cursor context manager not supported.
    """

    def __init__(self, mysql_connector_connection):
        self.connection = mysql_connector_connection
        self.cursor = None

    def __enter__(self):
        self.cursor = self.connection.cursor(buffered=True)
        return self.cursor

    def __exit__(self, exception_type, exception_value, traceback):
        self.cursor.close()


class ADSBDB:
    # TODO: Ad description of class
    pi = 3.14  # Magic constant

    # Form a string with table column names for further using in queries
    columns = '`Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, `longitude`, ' \
              '`latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`, `vertical_rate`, `sensors`, ' \
              '`geo_altitude`, `squawk`, `spi`, `position_source`'

    # Form a string with 'column=VALUES(column)' for further updating rows queries
    columns_list = columns.split(', ')
    columns_duplicate_key_update_query = ', '.join([f'{x}=VALUES({x})' for x in columns_list])

    # Queries #

    all_states_query = f'SELECT * FROM `current_flights`'

    certain_states_query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, ' \
                           f'`longitude`, `latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`,' \
                           f' `vertical_rate` FROM `current_flights`'

    def __init__(self, **kwargs):

        self.host = kwargs['host']
        self.database = kwargs['database']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.credentials = kwargs
        self.erased_states_count = 0
        self.errors = None
        self.response_status_code = None
        self.connection = self.connection()
        self.table_name = 'current_flights'

    @timer_logger
    def connection(self):

        try:

            return mysql.connector.connect(host=self.host, database=self.database, user=self.user,
                                           password=self.password, buffered=False, connect_timeout=10)

        except errors.Error as error:

            self.errors = error

        finally:

            pass

    def create_flight_states_table(self, table_name: str = None):
        """

        :type table_name: str
        """
        # TODO: Ad description oj function

        if table_name:
            self.table_name = table_name

        if self.errors is None:

            try:

                query = f'CREATE TABLE IF NOT EXISTS `{self.table_name}` (\n' \
                        f'  `Id` INT(11) NOT NULL,\n' \
                        f'  `icao24` CHAR(6) NULL DEFAULT NULL,\n' \
                        f'  `callsign` TINYTEXT NULL DEFAULT NULL,\n' \
                        f'  `origin_country` TINYTEXT NULL DEFAULT NULL,\n' \
                        f'  `time_position` INT(11) NULL DEFAULT NULL,\n' \
                        f'  `last_contact` INT(11) NULL DEFAULT NULL,\n' \
                        f'  `longitude` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `latitude` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `baro_altitude` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `on_ground` TINYINT(1) NULL DEFAULT NULL,\n' \
                        f'  `velocity` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `true_track` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `vertical_rate` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `sensors` INT(11) NULL DEFAULT NULL,\n' \
                        f'  `geo_altitude` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `squawk` TINYTEXT NULL DEFAULT NULL,\n' \
                        f'  `spi` FLOAT NULL DEFAULT NULL,\n' \
                        f'  `position_source` INT(11) NULL DEFAULT NULL,\n' \
                        f'  PRIMARY KEY (`Id`)\n' \
                        f')\n' \
                        f';'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(query)

                self.connection.commit()

            except errors.Error as error:

                self.errors = error

    def request_flight_states(self) -> list:

        """ Return all flight states from opensky-network.org API as a list of lists,
            None if errors or if bad response code.
            :rtype: list or None
        """

        try:
            response = requests.get(url)

            self.response_status_code = response.status_code

            if self.response_status_code == 200:
                flight_states = response.json()['states']
                # response.json()['time']
                return flight_states

        except (exceptions.ConnectionError, exceptions.ReadTimeout) as _error:  # exceptions.ConnectionError

            self.errors = _error

    @timer_logger
    def insert_flight_states(self):
        """
        Insert or update a flight states in to the database.
        :return: Error description or None if no errors
        :rtype: str or None

        """

        if not self.errors:

            # Get flight states from opensky-network.org API
            flight_states = self.request_flight_states()

            if flight_states:

                flight_state_values = []  # Create empty list for flight values

                for flight_state in flight_states[:]:  # Iterate over flight records

                    # Add new first element in list as decimal value of hex `icao24`
                    flight_state.insert(0, int(flight_state[0], 16))

                    for index, item in enumerate(flight_state):  # Iterate over enumerated flight values

                        if item is None:
                            flight_state[index] = 0  # Replace value to 0 if is None

                    # print(flight_state)
                    flight_state_values.append(flight_state[:])  # Add values to list

                # Perform list of values lists to list of values tuples
                flight_state_values = list(map(tuple, flight_state_values))

                # Truncate first and last symbols in string for SQL syntax
                values_query = str(flight_state_values)[1:-1]

                try:

                    # Form a query to insert all flight states in the table `table_name`
                    query = f'INSERT INTO {self.table_name} ({self.columns}) VALUES {values_query} ' \
                            f'ON DUPLICATE KEY UPDATE {self.columns_duplicate_key_update_query}'

                    with MySQLCursorContextManager(self.connection) as cursor:

                        cursor.execute(query)

                    self.connection.commit()

                except errors.Error as error:

                    self.errors = error

    @timer_logger
    def get_flight_states(self):

        """
        Get all flight states from a database.

        :return: List of flight states as a tuple of values
        :rtype: list or None
        """

        if self.errors is None:
            try:

                query = self.certain_states_query

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(query)
                    result = cursor.fetchall()

                    return result

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    def get_flight_states_paginate(self, start_row=0, rows_per_page=500):

        """
        Get all flight states from a database.

        :return: List of flight states as a tuple of values
        :rtype: list or None
        """

        if self.errors is None:
            try:

                query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, ' \
                        f'`longitude`, `latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`,' \
                        f' `vertical_rate` FROM `current_flights` LIMIT {start_row}, {rows_per_page}'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(query)
                    result = cursor.fetchall()

                    return result

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    @timer_logger
    def get_flight_states_count(self):

        """
        Get a count of all flight states from a database.

        :return: count of all flight states
        :rtype: int
        """

        if self.errors is None:
            try:

                # query = f'SELECT COUNT(`Id`) FROM `current_flights`'
                query = f'SELECT COUNT(*) FROM `current_flights`'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(query)
                    result = cursor.fetchall()
                    # result = cursor.fetchone()

                    return result[0][0]

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    @timer_logger
    def erase_lost_flight_states(self):

        """
        Get a count of all flight states from a database.

        :return: count of all flight states
        :rtype: int
        """

        if self.errors is None:
            try:

                # query = f'SELECT COUNT(`Id`) FROM `current_flights`'
                count_query = 'SELECT COUNT(*) FROM `current_flights` ' \
                              'WHERE `time_position` = 0 AND `longitude` = 0 AND `latitude` = 0 AND `baro_altitude` = 0'
                query = 'DELETE FROM `current_flights` ' \
                        'WHERE `time_position` = 0 AND `longitude` = 0 AND `latitude` = 0 AND `baro_altitude` = 0'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(count_query)
                    # result = cursor.fetchall()
                    self.erased_states_count = cursor.fetchone()[0]
                    cursor.execute(query)

                    # return result
                self.connection.commit()

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    @timer_logger
    def erase_expired_flight_states(self, minutes=3, seconds=0):

        """
        Erase a expired flight states from database.


        :return:
        :rtype:

        """

        if self.errors is None:
            try:

                time_now = datetime.utcnow().timestamp()
                expired_delta = timedelta(minutes=minutes, seconds=seconds).total_seconds()
                expired_time = int(time_now - expired_delta)

                # query = f'SELECT COUNT(`Id`) FROM `current_flights`'
                count_query = f'SELECT COUNT(*) FROM `current_flights` WHERE `time_position` < {expired_time}'
                query = f'DELETE FROM `current_flights` WHERE `time_position` < {expired_time}'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(count_query)
                    # result = cursor.fetchall()
                    self.erased_states_count = cursor.fetchone()[0]
                    cursor.execute(query)

                    # return result
                self.connection.commit()

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    def close(self):

        self.connection.close()

        pass


def update_database_loop(db_object, cycle_count=3, infinity=False, delay=0, ):
    logging.info(f'START database updating. Errors > {db_object.errors}')

    while db_object.errors is None and cycle_count != 0 or infinity:
        db_object.insert_flight_states()
        logging.info(f'UPDATING Errors > {db_object.errors} '
                     f'Response status code > {db_object.response_status_code}')
        adsbdb.erase_lost_flight_states()
        # print(db_object.erased_states_count)
        logging.info(f'UPDATING Errors > {db_object.errors} '
                     f'Erased states > {db_object.erased_states_count}')

        adsbdb.erase_expired_flight_states()
        # print(db_object.erased_states_count)
        logging.info(f'UPDATING Errors > {db_object.errors} '
                     f'Erased states > {db_object.erased_states_count}')

        cycle_count -= 1
        time.sleep(delay)

    logging.info(f'STOP database updating. Errors > {db_object.errors}')


if __name__ == '__main__':
    adsbdb = ADSBDB(**credentials)


    def expired_timestamp(minutes=0, seconds=0):
        time_now = datetime.utcnow().timestamp()
        expired_delta = timedelta(minutes=minutes, seconds=seconds).total_seconds()
        expired_time = int(time_now - expired_delta)
        return expired_time

    # update_database_loop(adsbdb, cycle_count=30, infinity=True, delay=10)
    print(adsbdb.get_flight_states_count())
    # adsbdb.erase_lost_flight_states()
    # print(adsbdb.erased_states_count)
    # print(adsbdb.erase_lost_flight_states())
    # time.sleep(1)
    # print(adsbdb.get_flight_states())
    # print(adsbdb.connection._connection_timeout)
    # print(adsbdb.connection.__dict__)
    # adsbdb.erase_expired_flight_states()
    # print(adsbdb.erased_states_count)
    # print(adsbdb.get_flight_states_paginate(3))
    # print(adsbdb.request_flight_states())
