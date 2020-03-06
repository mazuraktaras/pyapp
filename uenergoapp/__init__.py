from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ueuser:uepass@localhost:3306/uedatabase'

database = SQLAlchemy(app)


class Tags(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    asked_time = database.Column(database.DateTime, nullable=True)
    asked_url = database.Column(database.String(2048), nullable=True)
    tags = database.Column(database.JSON, nullable=True)

    def __repr__(self):
        return f'{self.asked_url}'

database.create_all()

# Views must be imported after app object created due Flask developers recommendation
from uenergoapp import views
