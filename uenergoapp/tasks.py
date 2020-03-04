# from __future__ import absolute_import, unicode_literals
import time

from uenergoapp.celapp import celapp
from bs4 import BeautifulSoup
import requests


@celapp.task()
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


@celapp.task()
def mess():
    return 2 + 2


@celapp.task()
def url_tags_counting(url):
    time.sleep(3)
    return url
