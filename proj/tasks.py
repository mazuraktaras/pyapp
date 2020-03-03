# from __future__ import absolute_import, unicode_literals
import time

from proj.celapp import celapp


@celapp.task()
def mess():
    return 2 + 2


@celapp.task()
def url_tags_counting(url):
    time.sleep(3)
    return url
