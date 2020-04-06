from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'bmnkvsk'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jwtblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'bmnkvsk'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_CSRF_CHECK_FORM'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['MY_CONF_PARM'] = 33
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ueuser:12345678@mysqlserver:3306/uedatabase'

database = SQLAlchemy(app)
blog_api = Api(app)
jwt = JWTManager(app)

# Views must be imported after app object created due Flask developers recommendation
from jwtblogapp import views, models
from jwtblogapp.resources import SignupUser, LoginUser, LogoutUser, Posts, PostRating

database.create_all()

blog_api.add_resource(SignupUser, '/api/signup')
blog_api.add_resource(LoginUser, '/api/login')
blog_api.add_resource(LogoutUser, '/api/logout')
blog_api.add_resource(Posts, '/api/posts')
blog_api.add_resource(PostRating, '/api/rating')
