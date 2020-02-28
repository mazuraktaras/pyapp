# -*- coding: utf-8 -*-

# from pprint import pprint

import functools
import sys
import time
from configparser import ConfigParser
import logging
import mysql.connector
from mysql.connector import errors
import requests
from requests import exceptions

# Read credentials from *.cfg file
config = ConfigParser()
config.read('adsbdb.cfg')
# Pack credentials to the dictionary
credentials = dict(config['MARIADB'])

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
        value = function(*args, **kwargs)
        stop = time.perf_counter()  # Get stop time

        logging.info(f'EXECUTING the function {function.__name__} in {stop - start} sec.')

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


class Cursor(MySQLCursorContextManager):
    def __exit__(self, exception_type, exception_value, traceback):
        self.cursor.close()
        # self.connection.close()
        print('Abandon', exception_type, exception_value, traceback)
        # raise Exception(exception_type).with_traceback(traceback)

        return True


class ADSBDB:
    # TODO: Ad description of class
    pi = 3.14  # Magic constant

    # Form a string with table column names for further queries
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
        self.errors = None
        self.response_status_code = None
        self.connection = self.connection()
        self.table_name = 'current_flights'

        pass

    def __init_(self, host='localhost', database='adsb', user='root', password='1234567-vV'):

        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.errors = None
        self.response_status_code = None
        self.connection = self.connection()
        self.table_name = 'current_flights'

        pass

    @timer_logger
    def connection(self):

        _connection = None

        try:

            _connection = mysql.connector.connect(host=self.host, database=self.database, user=self.user,
                                                  password=self.password, buffered=False)

        except errors.Error as _error:

            self.errors = _error

        finally:

            pass

        return _connection

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

            except errors.Error as _error:

                self.errors = _error

    @timer_logger
    def request_flight_states(self):

        """ Return all flight states from opensky-network.org API
            as list of lists, None if errors or if bad response code.
        """
        self.response_status_code = None
        flight_states = None

        try:
            response = requests.get('https://opensky-network.org/api/states/all')
            # response = requests.get('https://mazurak:1234567-vV@opensky-network.org/api/states/all')

        except (exceptions.ConnectionError, exceptions.ReadTimeout) as _error:  # exceptions.ConnectionError

            self.errors = _error

            return

        self.response_status_code = response.status_code
        if self.response_status_code is 200:
            flight_states = response.json()['states']
            # response.json()['time']
        else:
            pass

        return flight_states

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

    def insert_flight_states_old(self):
        # TODO: Add inserting/updating algorithm

        flight_states = self.request_flight_states()

        if flight_states is None:
            return
        else:

            flight_state_values = []  # Create empty list for flight values

            for flight_state in flight_states[:3]:  # Iterate over flight records

                # Add new first element in list as decimal value of hex `icao24`
                flight_state.insert(0, int(flight_state[0], 16))

                for index, item in enumerate(flight_state):  # Iterate over enumerated flight values

                    if item is None:
                        flight_state[index] = 0  # Replace value to 0 if is None

                print(flight_state)
                flight_state_values.append(flight_state[:])  # Add values to list

            # Perform list of values lists to list of values tuples
            flight_state_values = list(map(tuple, flight_state_values))

            values_query = str(flight_state_values)[1:-1]  # Truncate first and last symbols in string for SQL syntax
            print(values_query)
            # Form a query to insert all flight states in the table `table_name`
            query_state = f'INSERT INTO {self.table_name} ({self.columns}) VALUES {values_query} ' \
                          f'ON DUPLICATE KEY UPDATE {self.columns_duplicate_key_update_query}'

            print(query_state)

        if self.errors is None:
            _cursor = self.connection.cursor()
        else:
            return

        try:

            _cursor.execute(query_state)

        except errors.Error as _error:

            self.errors = _error
            _cursor.close()

        self.connection.commit()

        return

    @timer_logger
    def get_flight_states(self):

        _cursor = None

        if self.errors is None:
            _cursor = self.connection.cursor()
        else:
            return

        _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact` ' \
                 f'FROM `current_flights` WHERE `origin_country` = "South Africa" LIMIT 100'
        _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, ' \
                 f'`longitude`, `latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`, `vertical_rate` ' \
                 f'FROM `current_flights`'

        try:

            _cursor.execute(_query)

        except errors.Error as _error:

            self.errors = _error
            _cursor.close()

        # self.connection.commit()

        return _cursor.fetchall()

    def get_flight_states_new(self):

        """
        Get all flight states from a database.

        :return: List of flight states as a tuple of values
        :rtype: list or None
        """

        if self.errors is None:
            try:

                _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, ' \
                         f'`time_position`, `last_contact` ' \
                         f'FROM `current_flights` WHERE `origin_country` = "South Africa" LIMIT 100'

                _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, ' \
                         f'`longitude`, `latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`,' \
                         f' `vertical_rate` FROM `current_flights` LIMIT 3'

                query = self.certain_states_query

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

                _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, ' \
                         f'`time_position`, `last_contact` ' \
                         f'FROM `current_flights` WHERE `origin_country` = "South Africa" LIMIT 100'

                _query = f'SELECT `Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, ' \
                         f'`longitude`, `latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`,' \
                         f' `vertical_rate` FROM `current_flights` LIMIT 3'

                query = f'SELECT COUNT(`Id`) FROM `current_flights`'

                with MySQLCursorContextManager(self.connection) as cursor:

                    cursor.execute(query)
                    result = cursor.fetchall()

                    return result[0][0]

            except errors.Error as _error:

                self.errors = _error
                cursor.close()

    def close(self):

        pass


def update_database_loop(db_object, cycle_count=3, infinity=False, delay=0, ):
    logging.info(f'START database updating. Errors > {db_object.errors}')

    while db_object.errors is None and cycle_count != 0 or infinity:
        db_object.insert_flight_states()
        logging.info(f'UPDATING Errors > {db_object.errors}'
                     f'Response status code > {db_object.response_status_code}')
        cycle_count -= 1
        time.sleep(delay)

    logging.info(f'STOP database updating. Errors > {db_object.errors}')


if __name__ == '__main__':

    adsbdb = ADSBDB(**credentials)

    # update_database_loop(adsbdb, cycle_count=3, infinity=True)
    pathss = sys.path
    print(pathss)
    print(adsbdb.errors)
