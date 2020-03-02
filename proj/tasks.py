# from __future__ import absolute_import, unicode_literals
from proj.celapp import celapp


@celapp.task()
def mess():
    return 2 + 2
