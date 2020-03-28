from jwtblogapp import database
from passlib.hash import pbkdf2_sha512


class User(database.Model):
    __tablename__ = 'blog_users'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(128), unique=True)
    password = database.Column(database.String(128))
    created_time = database.Column(database.DateTime)

    def store(self):
        database.session.add(self)
        database.session.commit()

    @classmethod
    def del_all_users(cls):
        database.session.query(cls).delete()
        database.session.commit()

    def make_hash(self):
        self.password = pbkdf2_sha512.hash(self.password)

    def ensure_password(self, password):
        return pbkdf2_sha512.verify(password, self.password)

    def __repr__(self):
        return f'{self.username}'


class RevokedToken(database.Model):
    __tablename__ = 'revoked_tokens'

    id = database.Column(database.Integer, primary_key=True)
    jti = database.Column(database.String(128))

    # time = database.Column(database.DateTime, nullable=True)

    def store(self):
        database.session.add(self)
        database.session.commit()
