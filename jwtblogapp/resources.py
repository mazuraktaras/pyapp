from datetime import datetime
from flask_restful import Resource, reqparse
from .models import User, RevokedToken, Post, Rating
from sqlalchemy.exc import IntegrityError
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt, get_jwt_identity

# Instantiate the argument's parsers
auth_arguments_parser = reqparse.RequestParser()

blog_arguments_parser = reqparse.RequestParser()

rating_arguments_parser = reqparse.RequestParser()

# Add arguments for parsing
auth_arguments_parser.add_argument('username', required=True, help='Can not be blank')
auth_arguments_parser.add_argument('password', required=True, help='Can not be blank')

blog_arguments_parser.add_argument('post_text', required=True, help='Can not be blank')

rating_arguments_parser.add_argument('post_id', type=int, required=True, help='Can not be blank')
rating_arguments_parser.add_argument('like', type=int, required=True, help='Can not be blank')


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

    @staticmethod
    def get():
        posts_json = [{'post_id': post.id, 'user_id': post.user_id, 'post_text': post.text, 'likes': post.likes,
                       'dislikes': post.dislikes,
                       'created_time': str(post.created_time)
                       } for post in Post.query.all()]
        return {'posts': posts_json}

    @jwt_required
    def post(self):
        user = User.query.filter_by(username=get_jwt_identity()).first()
        arguments = blog_arguments_parser.parse_args()
        new_post = Post(user_id=user.id, text=arguments['post_text'], likes=0, dislikes=0, created_time=datetime.now())
        new_post.store()

        return {'message': 'Post successfully created'}


class PostRating(Resource):

    @jwt_required
    def post(self):

        post_like_id = None
        post_dislike_id = None
        post_id = None

        user = User.query.filter_by(username=get_jwt_identity()).first()
        arguments = rating_arguments_parser.parse_args()
        query_result = Rating.query.filter_by(user_id=user.id).all()

        if not Post.query.get(arguments['post_id']):
            return {'msg': 'Not such post_id in database'}

        if arguments['like'] == 1:
            post_like_id = arguments['post_id']

            if post_like_id in [result.post_like_id for result in query_result]:
                return {'msg': 'Post already liked by user'}

            post = Post.query.filter_by(id=arguments['post_id']).first()
            post.likes = Post.likes + 1
            if post_dislike_id in [result.post_dislike_id for result in query_result]:
                print('In dislikes')
                rating = Rating.query.filter_by(user_id=user.id, post_dislike_id=None).all()
            post.update()
        else:
            post_dislike_id = arguments['post_id']

            if post_dislike_id in [result.post_dislike_id for result in query_result]:
                return {'msg': 'Post already disliked by user'}
            post = Post.query.filter_by(id=arguments['post_id']).first()
            post.dislikes = Post.dislikes + 1
            post.update()

        new_rating = Rating(user_id=user.id, post_like_id=post_like_id, post_dislike_id=post_dislike_id,
                            created_time=datetime.now())
        new_rating.store()

        return {'message': 'Rating successfully created'}
