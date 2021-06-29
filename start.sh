#!/usr/bin/env bash

#  set -e -x

. venv/bin/activate

export FLASK_APP=blog.py

flask run --host=0.0.0.0 --port=8080



