from flask import render_template
from uenergoapp import app
from uenergoapp.adsbobject.adsbobject import ADSBDB, credentials

# from .adsbobject import *


@app.route('/')
def index():
    return render_template('ue_bootstrap.j2', title='UENERGO',
                           range_=['test', 'another', 'third', 'test', 'another', 'third', ])


@app.route('/flights')
def flights():
    database = ADSBDB(**credentials)
    flight_states = database.get_flight_states()
    flights_count = database.get_flight_states_count()
    database.close()
    return render_template('flights_adsb.html.j2', title='UENERGO Flights', flight_states=flight_states,
                           count=flights_count)

'''
@app.route('/jumbo')
def jumbo():
    response = database.get_flight_states()
    return render_template('index.html.j2', title='UENERGO',
                           range_=response, )
'''
                           

@app.route('/terminal')
def terminal():
    database = ADSBDB(**credentials)
    response = database.get_flight_states_count()
    database.close()
    # return app.config["TERMINAL"]
    return str(response)
