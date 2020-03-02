import time
from flask import Flask

# from flask import render_template
# from celery import Celery

app = Flask(__name__)


# celery = Celery(app.name, broker='redis://localhost:6379', backend='redis://localhost:6379')


# @celery.task(bind=True)
def simple_task(self):
    time.sleep(30)
    return


@app.route('/')
def index():
    print(app.name)
    task = simple_task.apply_async()
    return f'{task.id}'


@app.route('/status/<task_id>')
def status(task_id):
    task = simple_task.AsyncResult(task_id)
    task.get()
    return task.state


if __name__ == '__main__':
    app.run()
