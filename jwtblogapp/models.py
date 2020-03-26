from jwtblogapp import database
from passlib.hash import pbkdf2_sha256



class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    # asked_time = database.Column(database.DateTime, nullable=True)
    username = database.Column(database.String(128), unique=True, nullable=True)
    password = database.Column(database.String(128), nullable=True)

    # tags = database.Column(database.JSON, nullable=True)

    def __repr__(self):
        return f'{self.username}'

    def store(self):
        database.session.add(self)
        database.session.commit()

    @classmethod
    def del_all_users(cls):
        database.session.query(cls).delete()
        database.session.commit()

    def make_hash(password):
        return pbkdf2_sha256.hash(password)

