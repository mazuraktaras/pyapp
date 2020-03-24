from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jwtblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ueuser:12345678@mysqlserver:3306/uedatabase'

database = SQLAlchemy(app)
blog_api = Api(app)


class Tags(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    asked_time = database.Column(database.DateTime, nullable=True)
    asked_url = database.Column(database.String(2048), nullable=True)
    tags = database.Column(database.JSON, nullable=True)

    def __repr__(self):
        return f'{self.asked_url}'


database.create_all()

# Views must be imported after app object created due Flask developers recommendation
from jwtblogapp import views
from jwtblogapp.resources import RegUser, LogUser

blog_api.add_resource(RegUser, '/register')
blog_api.add_resource(LogUser, '/login')
