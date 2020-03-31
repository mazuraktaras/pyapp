import requests
from flask import flash, jsonify, make_response, request, render_template, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt, set_access_cookies, unset_jwt_cookies


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = StringField('Password')
    submit = SubmitField('Submit')


@app.before_first_request
def session_init():
    session['logged'] = False


@app.route('/')
# @jwt_required
def index():
    return render_template('blog_base.j2')
    # return str(url_for('loguser'))


@app.route('/websignup', methods=['GET', 'POST'])
def websignup():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        payload = {'username': username, 'password': password}
        response = requests.post('http://127.0.0.1:5000/signup', data=payload)

        if response.status_code == 202:
            form.username.data = ''
            form.password.data = ''
            flash(response.json()['message'])
            return redirect(url_for('websignup'))

        flash(response.json()['message'])
        return redirect('weblogin')

    return render_template('blog_signup.j2', form=form, name='')


@app.route('/weblogin', methods=['GET', 'POST'])
def weblogin():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        payload = {'username': username, 'password': password}
        response = requests.post('http://127.0.0.1:5000/login', data=payload)
        if response.status_code == 202:
            form.username.data = ''
            form.password.data = ''
            flash(response.json()['message'])
            return redirect(url_for('weblogin'))

        session['logged'] = True
        token = response.json()['token']
        form.username.data = 'tst'
        form.password.data = ''
        response = make_response(redirect(url_for('posts')))
        set_access_cookies(response, token)
        flash('Loged in. Here posts')
        return response

    return render_template('blog_signup.j2', form=form, name='')


@app.route('/weblogout', methods=['GET', 'POST'])
# @jwt_required
def weblogout():
    if not session['logged']:
        flash('User do not logged in yet')
        return redirect(url_for('index'))

    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    session['logged'] = False
    flash('You are successfully logged out')
    return response
    # return render_template('blog_posts.j2')


@app.route('/posts', methods=['GET', 'POST'])
# @jwt_required
def posts():
    return render_template('blog_posts.j2')
