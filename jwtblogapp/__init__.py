from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from jwtblogapp import config

app = Flask(__name__)

app.config.from_object(config)

database = SQLAlchemy(app)
blog_api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def session_init():
    database.create_all()
    session['logged'] = False


# Views must be imported after app object created due Flask developers recommendation
from jwtblogapp import views, models
from jwtblogapp.resources import SignupUser, LoginUser, LogoutUser, Posts, PostRating

blog_api.add_resource(SignupUser, '/api/signup')
blog_api.add_resource(LoginUser, '/api/login')
blog_api.add_resource(LogoutUser, '/api/logout')
blog_api.add_resource(Posts, '/api/posts')
blog_api.add_resource(PostRating, '/api/rating')
