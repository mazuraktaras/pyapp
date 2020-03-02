from flask import render_template, jsonify
from uenergoapp import app
from uenergoapp.adsbobject.adsbobject import ADSBDB, credentials
from bs4 import BeautifulSoup
import requests

# from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379', backend='redis://localhost:6379')


# @celery.task(bind=True)
def simple_task(self):
    return 'status'


@app.route('/')
def index():
    print(app.name)
    task = simple_task.apply_async()
    return task.id
