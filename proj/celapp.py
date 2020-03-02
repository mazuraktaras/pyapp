# from __future__ import absolute_import, unicode_literals
import proj.celeryconfig
from celery import Celery

# celapp = Celery('proj', broker='redis://localhost:6379', backend='redis://localhost:6379', include=['proj.tasks'], task_ignore_result=False)
celapp = Celery('proj', include=['proj.tasks'], task_ignore_result=False)
celapp.config_from_object(proj.celeryconfig)

# celery -A celapp worker -l info --pool=solo

if __name__ == '__main__':
    celapp.start()
