import requests
from flask import request, render_template, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])


@app.route('/')
# @jwt_required
def index():
    payload = {'username': 'mazurak', 'password': 'protractor'}
    response = requests.post('http://127.0.0.1:5000/login', data=payload)
    token = response.json()['token']
    return token
    # return render_template('ue_bootstrap.j2')
