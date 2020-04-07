from datetime import datetime
from flask_restful import Resource, reqparse
from .models import User, RevokedToken, Post, Rating
from sqlalchemy.exc import IntegrityError
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt, get_jwt_identity

# Instantiate the argument's parsers
auth_arguments_parser = reqparse.RequestParser()

post_arguments_parser = reqparse.RequestParser()

rating_arguments_parser = reqparse.RequestParser()

# Add arguments for parsing
auth_arguments_parser.add_argument('username', required=True, help='Can not be blank')
auth_arguments_parser.add_argument('password', required=True, help='Can not be blank')

post_arguments_parser.add_argument('post_text', required=True, help='Can not be blank')

rating_arguments_parser.add_argument('post_id', type=int, required=True, help='Can not be blank')
rating_arguments_parser.add_argument('like', type=int, required=True, help='Can not be blank')


@jwt.token_in_blacklist_loader
def if_blacklisted(decrypted_token):
    jti = decrypted_token['jti']
    return bool(RevokedToken.query.filter_by(jti=jti).first())


# define a class for user registration
class SignupUser(Resource):

    @staticmethod
    def post():

        arguments = auth_arguments_parser.parse_args()
        new_user = User(username=arguments['username'], password=arguments['password'])
        new_user.make_hash()

        try:
            new_user.store()
            return {'msg': f'User {new_user.username} successfully signed up'}
        except IntegrityError:
            return {'msg': f'User {new_user.username} already exist'}, 202


# define a class for user login
class LoginUser(Resource):

    @staticmethod
    def post():

        arguments = auth_arguments_parser.parse_args()
        if not User.query.filter_by(username=arguments['username']).first():

            return {'msg': 'Bad credentials! Login again or signup'}, 401

        else:
            user = User.query.filter_by(username=arguments['username']).first()

            if user.ensure_password(arguments['password']):

                token = create_access_token(identity=user.username)

                return {'msg': f'User {arguments["username"]} successfully logged in', 'token': token}
            else:
                return {'msg': 'Bad credentials! Login again or signup'}, 401


# define a class for user logout
class LogoutUser(Resource):

    @jwt_required
    def post(self):
        revoked_token = RevokedToken(jti=get_raw_jwt()['jti'])
        revoked_token.store()
        return {'msg': 'You are successfully logged out'}


class Posts(Resource):

    @jwt_required
    def get(self):
        posts_json = [{'post_id': post.id, 'user_id': post.user_id, 'username': post.username, 'post_text': post.text,
                       'likes': post.likes,
                       'dislikes': post.dislikes,
                       'created_time': post.created_time.strftime("%d-%m-%Y %H:%M:%S")
                       } for post in Post.query.all()]
        return {'posts': posts_json}

    @jwt_required
    def post(self):
        user = User.query.filter_by(username=get_jwt_identity()).first()
        arguments = post_arguments_parser.parse_args()
        new_post = Post(user_id=user.id, username=user.username, text=arguments['post_text'], likes=0, dislikes=0,
                        created_time=datetime.now())
        new_post.store()

        return {'msg': 'Post successfully created'}


class PostRating(Resource):

    @jwt_required
    def post(self):

        post_like_id = None
        post_dislike_id = None

        user = User.query.filter_by(username=get_jwt_identity()).first()
        arguments = rating_arguments_parser.parse_args()
        post_id = arguments['post_id']

        query_result = Rating.query.filter_by(user_id=user.id).all()

        if not Post.query.get(post_id):
            return {'msg': 'Not such post_id in database'}, 404

        post = Post.query.filter_by(id=post_id).first()

        if arguments['like'] == 1:

            # print([result.post_like_id for result in query_result])
            if post_id in [result.post_like_id for result in query_result]:
                return {'msg': f'Post already liked by {user.username}'}, 202

            if post_id in [result.post_dislike_id for result in query_result]:
                rating = Rating.query.filter_by(user_id=user.id, post_dislike_id=post_id).one()
                rating.post_dislike_id = None
                rating.post_like_id = post_id
                rating.update()

                post.likes = Post.likes + 1
                post.dislikes = Post.dislikes - 1
                post.update()

                return {'msg': 'Rating updated to LIKE'}

            post.likes = Post.likes + 1
            post_like_id = post_id

        else:

            if post_id in [result.post_dislike_id for result in query_result]:
                return {'msg': f'Post already disliked by {user.username}'}, 202

            if post_id in [result.post_like_id for result in query_result]:
                rating = Rating.query.filter_by(user_id=user.id, post_like_id=post_id).one()
                rating.post_like_id = None
                rating.post_dislike_id = post_id
                rating.update()

                post.dislikes = Post.dislikes + 1
                post.likes = Post.likes - 1
                post.update()

                return {'msg': 'Rating updated to DISLIKE'}

            post.dislikes = Post.dislikes + 1
            post_dislike_id = post_id

        post.update()

        new_rating = Rating(user_id=user.id, post_like_id=post_like_id, post_dislike_id=post_dislike_id,
                            created_time=datetime.now())
        new_rating.store()

        return {'msg': 'Rating successfully created'}
