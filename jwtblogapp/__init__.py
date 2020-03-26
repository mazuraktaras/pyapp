from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jwtblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ueuser:12345678@mysqlserver:3306/uedatabase'

database = SQLAlchemy(app)
blog_api = Api(app)

# Views must be imported after app object created due Flask developers recommendation
from jwtblogapp import views, models
from jwtblogapp.resources import RegUser, LogUser, AllUsers

database.create_all()

blog_api.add_resource(RegUser, '/register')
blog_api.add_resource(LogUser, '/login')
blog_api.add_resource(AllUsers, '/all')
