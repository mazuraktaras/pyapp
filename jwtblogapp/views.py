import requests
from flask import request, render_template, redirect, session, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = StringField('Password')
    submit = SubmitField('Submit')


@app.route('/')
# @jwt_required
def index():
    payload = {'username': 'mazurak', 'password': 'protractor'}
    response = requests.post('http://127.0.0.1:5000/login', data=payload)
    token = response.json()['token']
    # TODO: return str(url_for(AllUsers))
    # return render_template('blog_base.j2')
    return str(url_for('loguser'))


@app.route('/weblogin', methods=['GET', 'POST'])
# @jwt_required
def weblogin():
    token = None
    form = LoginForm()
    username = None
    # username = 'email'

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        payload = {'username': username, 'password': password}
        response = requests.post('http://127.0.0.1:5000/login', data=payload)
        token = response.json()['token']
        form.username.data = ''
        form.password.data = ''

    return render_template('blog_base.j2', form=form, name=token)
    # return str(app.url_map)
