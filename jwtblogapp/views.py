import requests
from flask import flash, jsonify, make_response, request, render_template, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt, set_access_cookies, \
    unset_jwt_cookies


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign me up')


class PostForm(FlaskForm):
    post_text = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')


class RateForm(FlaskForm):
    post_id = HiddenField()
    like = HiddenField()
    # submit = SubmitField('Like')


@app.before_first_request
def session_init():
    session['logged'] = False


@app.route('/')
def index():
    return render_template('blog_base.j2')


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
    form.submit.label.text = 'Login'

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

    return render_template('blog_login.j2', form=form, name='')


@app.route('/weblogout', methods=['GET', 'POST'])
@jwt_required
def weblogout():
    if not session['logged']:
        flash('User do not logged in yet')
        return redirect(url_for('index'))

    token = request.cookies.get('access_token_cookie')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://127.0.0.1:5000/logout', headers=headers)
    print(response.status_code)

    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    session['logged'] = False
    flash('You are successfully logged out')
    return response


@app.route('/posts', methods=['GET', 'POST'])
# @jwt_required
def posts():
    # current_user = get_jwt_identity()

    # print(current_user)

    form = PostForm()
    rate_form = RateForm()
    print(rate_form.data)
    print(form.data)

    if rate_form.is_submitted() and rate_form.like.data:
        print('Submited Rate')
        post_id = rate_form.post_id.data
        like = rate_form.like.data
        token = request.cookies.get('access_token_cookie')
        headers = {'Authorization': f'Bearer {token}'}
        payload = {'post_id': post_id, 'like': like}
        print(payload)
        response = requests.post('http://127.0.0.1:5000/rating', headers=headers, data=payload)
        flash(response.text)
        return redirect(url_for('posts'))

    if form.validate_on_submit():
        post_text = form.post_text.data

        token = request.cookies.get('access_token_cookie')
        headers = {'Authorization': f'Bearer {token}'}

        payload = {'post_text': post_text}
        print(payload)
        response = requests.post('http://127.0.0.1:5000/blog', headers=headers, data=payload)
        flash(response.text)
        return redirect(url_for('posts'))

    response = requests.get('http://127.0.0.1:5000/blog')
    posts_ = response.json()['posts']
    # print(posts)
    return render_template('blog_posts.j2', form=form, rate_form=rate_form, posts=posts_)
