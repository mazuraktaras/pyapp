import json
from datetime import datetime
from uenergoapp import database, Tags
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
    tags_count_list = \
        [{'tag_name': key, 'tag_count': value} for key, value in
         {tag.name: len(soup.find_all(tag.name)) for tag in all_tags}.items()]

    tags_row = Tags(asked_time=datetime.now(), asked_url=url, tags=json.dumps(tags_count_list))
    database.session.add(tags_row)
    database.session.commit()
    return tags_count_list
