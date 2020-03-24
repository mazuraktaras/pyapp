from flask import request, render_template, url_for, jsonify

from jwtblogapp import app


@app.route('/')
def index():
    return jsonify({'message': 'Entry point'})
