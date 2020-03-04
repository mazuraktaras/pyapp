# from __future__ import absolute_import, unicode_literals
import uenergoapp.celeryconfig
from celery import Celery

# celapp = Celery('proj', broker='redis://localhost:6379', backend='redis://localhost:6379', include=['proj.tasks'])
celapp = Celery('uenergoapp', include=['uenergoapp.tasks'], task_ignore_result=False)
celapp.config_from_object(uenergoapp.celeryconfig)

# celery -A uenergoapp.celapp worker -l info --pool=solo

if __name__ == '__main__':
    celapp.start()
