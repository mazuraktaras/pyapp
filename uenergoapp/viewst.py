from flask import request, render_template, url_for, jsonify

from proj.tasks import mess, url_tags_counting
from uenergoapp import app


# from uenergoapp.adsbobject.adsbobject import ADSBDB, credentials
# from bs4 import BeautifulSoup
# import requests
# import proj


# from celery import Celery


# @celery.task(bind=True)
def simple_task(self):
    return 'status'


@app.route('/')
def index():
    return render_template('ue_ajax.j2')


@app.route('/start', methods=['POST'])
def start():
    tag_task = url_tags_counting.delay('urly')
    return jsonify({}), 202, {'Location': url_for('task_state', task_id=tag_task.id)}


@app.route('/start2', methods=['POST', 'GET'])
def start2(url='TestURL'):
    url = request.form['name']

    return jsonify({'url': url}), 202, {'Location': url}


@app.route('/task_state/<task_id>')
def task_state(task_id):
    tag_task = url_tags_counting.AsyncResult(task_id)
    return tag_task.state


if __name__ == '__main__':
    pass
    tag_task = mess.delay()
    print(type(tag_task.state), tag_task.state)

'''res = mess.delay()
# sleep(2)
while res.state != 'SUCCESS':
    print('Wait', res.state)
    print(type(res.state), res.state)
print(res.get(timeout=1))
'''
