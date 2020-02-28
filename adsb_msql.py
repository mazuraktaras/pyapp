import mysql.connector
import json

jsonfile = 'AircraftList.json'
table_name = 'flights7'


def flights_table_columns(name_, cursor_):
    # TODO: Add variable table nam possibility

    cursor_.execute(f'DESCRIBE {name_}')
    dscr_list = cursor_.fetchall()
    columns_name_list = [column_item[0] for column_item in dscr_list]

    return columns_name_list


def create_flights_table(name_, json_file, restricted_msql):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:

            data = json.load(file)

    except FileNotFoundError as err:
        print(err)

    max_item_len = 1
    max_item = None

    for item in data['acList']:
        if len(item) >= max_item_len:
            max_item = item
            max_item_len = len(item)
        else:
            pass

    string = ''

    for key in max_item.keys():
        if type(max_item[key]) is int:
            type_ = 'BIGINT'

        elif type(max_item[key]) is float:
            type_ = 'FLOAT'

        elif type(max_item[key]) is bool:
            type_ = 'BOOL'

        else:
            type_ = 'TEXT'

        if (key.upper(),) in restricted_msql:

            key = f'`{key}`'

        else:
            pass

        column_list = [key, type_]
        column_name = ' '.join(column_list)

        string = string + ', ' + column_name

        # print(string)

    string = string  # + ', Tag TINYTEXT'
    query_ = f'CREATE TABLE {name_} (RecNum INT AUTO_INCREMENT PRIMARY KEY{string})'

    return query_


def insert_flights_rows(name_, json_file, restricted_msql, cursor_):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:

            data = json.load(file)

    except FileNotFoundError as err:
        print(err)

    flight_records = data['acList']

    print(len(flight_records))
    query_list = []
    columns_names = flights_table_columns(table_name, cursor_)

    for record in flight_records[:]:

        columns_list = []
        columns_values_list = []

        print(flight_records.index(record))

        for key in record:

            if key not in columns_names:

                # print('HEEEEEEEEEEEEEEE', key)
                continue

            else:
                pass

            if (key.upper(),) in restricted_msql:

                column_name = f'`{key}`'

            else:
                column_name = key

            columns_list.append(column_name)

            if type(record[key]) is list:
                # print('IS---------->', key, f'{record[key]}')
                columns_values_list.append(f'{record[key]}')
            else:
                columns_values_list.append(record[key])

        columns_query = ', '.join(columns_list)

        values_query = str(columns_values_list)[1:-1]

        query_item = f'INSERT INTO {name_} ({columns_query}) VALUES ({values_query})'
        # print(query_item)

        cursor_.execute(query_item)

        query_list = None  # .append(query_item)
    # print(query_list)

    return query_list


def create_flight_states_table(table_name_, cursor_):
    print(table_name_)
    query__ = f'CREATE TABLE `{table_name_}` (\n' \
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
    print(query__)
    cursor_.execute(query__)


connection = mysql.connector.connect(host='localhost', database='adsb', user='root', password='1234567-vV')
connection.autocommit = False
connection.get_warnings = True
cursor = connection.cursor()

# query = 'SELECT name FROM mysql.help_keyword'

query = f'CREATE TABLE `flightsc` (\
    `Id` INT(11) NOT NULL,\
    `icao24` CHAR(6) NULL DEFAULT NULL,\
    `callsign` TINYTEXT NULL DEFAULT NULL,\
    `origin_country` TINYTEXT NULL DEFAULT NULL,\
    `time_position` INT(11) NULL DEFAULT NULL,\
    `last_contact` INT(11) NULL DEFAULT NULL,\
    `longitude` FLOAT NULL DEFAULT NULL,\
    `latitude` FLOAT NULL DEFAULT NULL,\
    `baro_altitude` FLOAT NULL DEFAULT NULL,\
    `on_ground` TINYINT(1) NULL DEFAULT NULL,\
    `velocity` FLOAT NULL DEFAULT NULL,\
    `true_track` FLOAT NULL DEFAULT NULL,\
    `vertical_rate` FLOAT NULL DEFAULT NULL,\
    `sensors` INT(11) NULL DEFAULT NULL,\
    `geo_altitude` FLOAT NULL DEFAULT NULL,\
    `squawk` TINYTEXT NULL DEFAULT NULL,\
    `spi` FLOAT NULL DEFAULT NULL,\
    `position_source` INT(11) NULL DEFAULT NULL,\
    PRIMARY KEY (`Id`)\
) \
COLLATE=\'utf8_general_ci\' \
ENGINE=InnoDB\
;'
# print(query)
# cursor.execute(query)

print(cursor.fetchwarnings())
# print(cursor.fetchall())


create_flight_states_table(table_name, cursor)
# print(query)
# cursor.execute(query)
# rows = cursor.fetchall()
# print(rows)


# quer = create_flights_table(table_name, jsonfile, restricted_msql=rows)
# cursor.execute(quer)
# print(quer)
# connection.commit()

# insert_flights_rows(table_name, jsonfile, rows, cursor)

# print(lis)
# print(quer)

# print(flights_table_columns(cursor))

cursor.close()
connection.commit()
connection.close()
