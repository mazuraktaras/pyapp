from datetime import datetime
from flask_restful import Resource, reqparse
from .models import User, RevokedToken, Post
from sqlalchemy.exc import IntegrityError
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt, get_jwt_identity

# Instantiate the argument's parser
auth_arguments_parser = reqparse.RequestParser()

blog_arguments_parser = reqparse.RequestParser()

# Add arguments for parsing
auth_arguments_parser.add_argument('username', required=True, help='Can not be blank')
auth_arguments_parser.add_argument('password', required=True, help='Can not be blank')

blog_arguments_parser.add_argument('post_text', required=True, help='Can not be blank')


@jwt.token_in_blacklist_loader
def if_blacklisted(decrypted_token):
    jti = decrypted_token['jti']
    return bool(RevokedToken.query.filter_by(jti=jti).first())


# define a class for user registration
class RegUser(Resource):

    # @staticmethod
    def post(self):

        arguments = auth_arguments_parser.parse_args()
        fresh_user = User(username=arguments['username'], password=arguments['password'])
        fresh_user.make_hash()

        try:
            fresh_user.store()
            return {'message': f'User {fresh_user.username} successfully signed up'}
        except IntegrityError:
            return {'message': f'User {fresh_user.username} already exist'}, 202


# define a class for user login
class LogUser(Resource):

    def post(self):

        arguments = auth_arguments_parser.parse_args()
        if not User.query.filter_by(username=arguments['username']).first():

            return {'message': 'No such user. Login again or signup'}, 202

        else:
            user = User.query.filter_by(username=arguments['username']).first()

            if user.ensure_password(arguments['password']):

                token = create_access_token(identity=user.username)

                return {'message': 'Successfully logged', 'token': token}
            else:
                return {'message': 'Bad password'}


# define a class for user logout
class LogoutUser(Resource):

    @jwt_required
    def post(self):
        revoked_token = RevokedToken(jti=get_raw_jwt()['jti'])
        revoked_token.store()
        return {'message': 'Logout'}


# define a class for all users actions
class AllUsers(Resource):

    # @jwt_required
    def get(self):
        users_json = [{'username': user.username, 'password': user.password} for user in User.query.all()]
        # print(get_raw_jwt())
        return {'users': users_json}

    @staticmethod
    @jwt_required
    def delete():
        User.del_all_users()

        return {'message': 'All users in the database have been deleted'}


class Blog(Resource):

    def get(self):
        posts_json = [{'user_id': post.user_id, 'post_text': post.text, 'created_time': str(post.created_time)
                       } for post in Post.query.all()]
        return {'posts': posts_json}

    @jwt_required
    def post(self):
        user = User.query.filter_by(username=get_jwt_identity()).first()
        arguments = blog_arguments_parser.parse_args()
        new_post = Post(user_id=user.id, text=arguments['post_text'], created_time=datetime.now())
        new_post.store()

        return {'message': 'Post successfully created'}
