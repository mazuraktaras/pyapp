import requests
from flask import flash, jsonify, make_response, request, render_template, redirect, session, url_for

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies

from jwtblogapp.forms import LoginForm, PostForm, RateForm
from jwtblogapp.bot import BlogBot


@jwt.expired_token_loader
def expired_token(callback):
    if request.user_agent.browser:
        response = make_response(redirect(url_for('index')))
        session['logged'] = False
        flash('You token is expired, please LogIn', 'danger')
        return response
    return jsonify(msg='Token has expired'), 401


@jwt.unauthorized_loader
def unauthorized_token(callback):
    if request.user_agent.browser:
        response = make_response(redirect(url_for('index')))
        session['logged'] = False
        flash('Your token is unauthorized! LogIn, please', 'danger')
        return response
    return jsonify(msg='Your token is unauthorized!'), 401


@app.route('/')
def index():
    return render_template('blog_base.j2')


@app.route('/web/signup', methods=['GET', 'POST'])
def web_signup():
    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        payload = {'username': username, 'password': password}
        response = requests.post(url_for('signupuser', _external=True), data=payload)

        if response.status_code == 202:
            form.username.data = ''
            form.password.data = ''
            flash(response.json()['msg'], 'danger')
            return redirect(url_for('web_signup'))

        flash(response.json()['msg'], 'success')
        return redirect(url_for('web_login'))

    return render_template('blog_signup.j2', form=form)


@app.route('/web/login', methods=['GET', 'POST'])
def web_login():
    form = LoginForm()
    form.submit.label.text = 'Login'

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        payload = {'username': username, 'password': password}
        response = requests.post(url_for('loginuser', _external=True), data=payload)

        if response.status_code == 401:
            flash(response.json()['msg'], 'danger')
            return redirect(url_for('web_login'))
        flash(response.json()['msg'], 'success')
        session['logged'] = True
        token = response.json()['token']
        form.username.data = 'eryteyr'
        form.password.data = ''
        response = make_response(redirect(url_for('blog')))
        set_access_cookies(response, token)

        return response

    return render_template('blog_login.j2', form=form)


@app.route('/web/logout', methods=['GET', 'POST'])
@jwt_required
def web_logout():
    token = request.cookies.get('access_token_cookie')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url_for('logoutuser', _external=True), headers=headers)
    flash(response.json()['msg'], 'warning')

    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    session['logged'] = False

    return response


@app.route('/web/blog', methods=['GET', 'POST'])
@jwt_required
def blog():
    current_user = get_jwt_identity()

    form = PostForm()
    rate_form = RateForm()

    token = request.cookies.get('access_token_cookie')
    headers = {'Authorization': f'Bearer {token}'}

    if rate_form.is_submitted() and rate_form.like.data:
        post_id = rate_form.post_id.data
        like = rate_form.like.data

        payload = {'post_id': post_id, 'like': like}

        response = requests.post(url_for('postrating', _external=True), headers=headers, data=payload)
        if response.status_code == 202:
            flash(response.json()['msg'], 'warning')
            return redirect(url_for('blog'))

        flash(response.json()['msg'], 'success')

        return redirect(url_for('blog'))

    if form.validate_on_submit():
        post_text = form.post_text.data

        payload = {'post_text': post_text}

        response = requests.post(url_for('posts', _external=True), headers=headers, data=payload)
        flash(response.json()['msg'])
        return redirect(url_for('blog'))

    response = requests.get(url_for('posts', _external=True), headers=headers)
    blog_posts = response.json()['posts']

    return render_template('blog_posts.j2', user=current_user, form=form, rate_form=rate_form, posts=blog_posts)


@app.route('/web/bot')
@jwt_required
def bot():
    blog_bot = BlogBot(number_of_users=app.config['BOT_NUMBER_OF_USERS'],
                       max_posts_per_user=app.config['BOT_MAX_POSTS_PER_USER'],
                       max_likes_per_user=app.config['BOT_MAX_LIKES_PER_USER'])
    blog_bot.background_run()
    flash('Bot started', 'success')
    return redirect(request.referrer)
