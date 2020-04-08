from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from jwtblogapp import config

# Initialize application object
app = Flask(__name__)

# Configure app from python object i.e. from python module (config.py)
app.config.from_object(config)

# Initialize database object
database = SQLAlchemy(app)
# Initialize api object
blog_api = Api(app)
# Initialize JWT support object
jwt = JWTManager(app)


# Before first request from frontend
@app.before_first_request
def session_init():
    """
    Before a first request from front end,
    create the database and tables if not exist.
    Assigns a 'True' value to session['logged'] property for
    further checking if user has been logged or not.
    """
    database.create_all()
    session['logged'] = False


# All that modules must be imported after app object created due Flask developers recommendation
from jwtblogapp import views, models
from jwtblogapp.resources import SignupUser, LoginUser, LogoutUser, Posts, PostRating

# Create endpoints with paths by adding resource classes
blog_api.add_resource(SignupUser, '/api/signup')
blog_api.add_resource(LoginUser, '/api/login')
blog_api.add_resource(LogoutUser, '/api/logout')
blog_api.add_resource(Posts, '/api/posts')
blog_api.add_resource(PostRating, '/api/rating')
