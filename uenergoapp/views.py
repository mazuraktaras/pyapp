from flask import render_template, jsonify
from uenergoapp import app
from uenergoapp.adsbobject.adsbobject import ADSBDB, credentials
from bs4 import BeautifulSoup
import requests


# from .adsbobject import *


def parse_html_tags(url: str) -> list:
    """
    Parse html document to find each tag count

    :param url: URL for parsing
    :return: A dictionary of tag:count pairs
    """
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    all_tags = soup.find_all()
    # tags_count_dictionary = {tag.name: len(soup.find_all(tag.name)) for tag in all_tags}
    tags_count_dictionary = \
        [{'tag_name': key, 'tag_count': value} for key, value in
         {tag.name: len(soup.find_all(tag.name)) for tag in all_tags}.items()]

    return tags_count_dictionary


@app.route('/')
def index():
    return render_template('ue_bootstrap.j2', title='UENERGO',
                           range_=['test', 'another', 'third', 'test', 'another', 'third', ])


@app.route('/tagscount', methods=['GET', 'POST'])
def tagscount():
    url_ = 'https://www.python.org'

    return jsonify(parse_html_tags(url_))


@app.route('/chart')
def chart():
    return render_template('ue_canvasjs.j2')


@app.route('/terminal')
def terminal():
    database = ADSBDB(**credentials)
    response = database.get_flight_states_count()
    database.close()
    # return app.config["TERMINAL"]
    return str(response)
