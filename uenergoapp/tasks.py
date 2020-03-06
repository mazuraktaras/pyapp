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
    :return: A list of dictionaries {tag_name: tag, tag_count: count}
    """
    # Make a request
    request = requests.get(url)
    # Parse a html and find all tags
    soup = BeautifulSoup(request.text, 'html.parser')
    all_tags = soup.find_all()

    # Count tags and make list of dictionaries for JSON
    tags_count_list = \
        [{'tag_name': key, 'tag_count': value} for key, value in
         {tag.name: len(soup.find_all(tag.name)) for tag in all_tags}.items()]

    # Instantiate DB Model with parameters
    tags_row = Tags(asked_time=datetime.now(), asked_url=url, tags=json.dumps(tags_count_list))
    # Add record to database
    database.session.add(tags_row)
    # Commit save record
    database.session.commit()
    return tags_count_list
