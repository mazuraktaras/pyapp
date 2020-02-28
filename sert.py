import requests
import mysql.connector
import json
import time

# import folium

# import timeit

jsonfile = "all2.json"
table_name = 'test72'

columns = '`Id`, `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, `longitude`, ' \
          '`latitude`, `baro_altitude`, `on_ground`, `velocity`, `true_track`, `vertical_rate`, `sensors`, ' \
          '`geo_altitude`, `squawk`, `spi`, `position_source`'
columns_list = columns.split(', ')
columns_duplicate_key_update_query = ', '.join([f'{x}=VALUES({x})' for x in columns_list])


def insert_flights_rows_json(name, json_file, cursor):
    """ Get """

    try:
        with open(json_file, 'r', encoding='utf-8') as file:

            data = json.load(file)

    except FileNotFoundError as err:
        print(err)

    flight_records = data['states']  # Get slice with flight records

    flight_state_values = []  # Create empty list for flight values

    for flight_state in flight_records[:2]:  # Iterate over flight records
        flight_state.insert(0, int(flight_state[0], 16))  # Add new first element in list as decimal `icao24`
        for index, item in enumerate(flight_state):  # Iterate over enumerated flight values

            if item is None:
                flight_state[index] = 0  # Replace value to 0 if is None

        flight_state_values.append(flight_state[:-7])  # Add values to list

    flight_state_values = list(map(tuple, flight_state_values))  # Perform list of values lists to list of values tuples

    values_query = str(flight_state_values)[1:-1]  # Truncate  first and  last symbols in string for SQL syntax

    # Form query to insert all flight states in table `name`
    query_state = f'INSERT INTO {name} ({columns}) VALUES {values_query} ON DUPLICATE KEY UPDATE Id=VALUES(Id), ' \
                  f'icao24=VALUES(icao24), callsign=VALUES(callsign), origin_country=VALUES(origin_country), ' \
                  f'time_position=VALUES(time_position), last_contact=VALUES(last_contact), longitude=VALUES(longitude), ' \
                  f'latitude=VALUES(latitude), baro_altitude=VALUES(baro_altitude), on_ground=VALUES(on_ground), ' \
                  f'velocity=VALUES(velocity)'

    print(query_state)
    # cursor.execute(query_state)  # Execute query


def get_flight_states():

    """ Return all flight states from opensky-network.org API
        in list of lists format
    """

    # response = requests.get('https://opensky-network.org/api/states/all')
    response = requests.get('https://mazurak:1234567-vV@opensky-network.org/api/states/all')

    # print(response.status_code)
    # print(response.json()['time'])

    flight_states = response.json()['states']

    return flight_states


def insert_flights_rows(name, flight_records, cursor):
    flight_state_values = []  # Create empty list for flight values

    for flight_state in flight_records[:]:  # Iterate over flight records
        flight_state.insert(0, int(flight_state[0], 16))  # Add new first element in list as decimal `icao24`
        # TODO: Modify comentx
        for index, item in enumerate(flight_state):  # Iterate over enumerated flight values

            if item is None:
                flight_state[index] = 0  # Replace value to 0 if is None

        # print(flight_state)
        flight_state_values.append(flight_state[:])  # Add values to list

    flight_state_values = list(map(tuple, flight_state_values))  # Perform list of values lists to list of values tuples

    values_query = str(flight_state_values)[1:-1]  # Truncate  first and  last symbols in string for SQL syntax

    # Form query to insert all flight states in table `name`
    _query_state = f'INSERT INTO {name} ({columns}) VALUES {values_query} ON DUPLICATE KEY UPDATE Id=VALUES(Id), ' \
                  f'icao24=VALUES(icao24), callsign=VALUES(callsign), origin_country=VALUES(origin_country), ' \
                  f'time_position=VALUES(time_position), last_contact=VALUES(last_contact), ' \
                  f'longitude=VALUES(longitude), latitude=VALUES(latitude), baro_altitude=VALUES(baro_altitude), ' \
                  f'on_ground=VALUES(on_ground), velocity=VALUES(velocity)'



    query_state = f'INSERT INTO {name} ({columns}) VALUES {values_query} ' \
                  f'ON DUPLICATE KEY UPDATE {columns_duplicate_key_update_query}'

    print(query_state)

    cursor.execute(query_state)  # Execute query


def get_flights_data(cursor):
    cursor.execute('SELECT `icao24`, `callsign`, `latitude`, `longitude`, `on_ground` FROM flightsb LIMIT 10')
    data = cursor.fetchall()
    return data


connection = mysql.connector.connect(host='localhost', database='adsb', user='root', password='1234567-vV')
connection.autocommit = False
curs = connection.cursor()

"""

adsmmap = folium.Map(location=[50.1079, 14.2571], zoom_start=8)

for i in range(0, 0):
    print(i)
    start_time = time.time()
    flight_records_ = get_flights_rows_req()
    end_time = time.time() - start_time
    print(end_time)
    start_time = time.time()
    insert_flights_rows(table_name, flight_records_, curs)
    curs.execute('COMMIT')
    end_time = time.time() - start_time
    print(end_time)
    time.sleep(0)

# insert_flights_rows(table_name, t, curs)

start_time = time.time()
for item in get_flights_data(curs):
    location = list(item[2:4])
    # print(item[2:4])
    # print(item[0:2])
    if item[4] == 0:
        folium.CircleMarker(location=location, color='#2b8cbe', weight=2, radius=5,
                            fill=True, fillColor='#2b8cbe', popup=item[1]).add_to(adsmmap)
    else:
        folium.CircleMarker(location=location, color='#ca0020', weight=2, radius=5,
                            fill=True, fillColor='#ca0020', popup='<p style="font-family: Candara"> Flight information</p>').add_to(adsmmap)

adsmmap.save('index.html')

end_time = time.time() - start_time
print(end_time)"""

start_time = time.time()
get_flight_states()
# insert_flights_rows(table_name, get_flight_states(), curs)
end_time = time.time() - start_time
print(end_time)

curs.close()
connection.commit()
connection.close()
