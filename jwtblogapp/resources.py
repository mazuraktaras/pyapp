from flask_restful import Resource, reqparse
from .models import User, RevokedToken
from sqlalchemy.exc import IntegrityError
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt  # get_jwt_identity

# Instantiate the argument's parser
arguments_parser = reqparse.RequestParser()

# Add arguments for parsing
arguments_parser.add_argument('username', required=True, help='Can not be blank')
arguments_parser.add_argument('password', required=True, help='Can not be blank')


@jwt.token_in_blacklist_loader
def if_blacklisted(decrypted_token):
    jti = decrypted_token['jti']
    return bool(RevokedToken.query.filter_by(jti=jti).first())


# define a class for user registration
class RegUser(Resource):

    # @staticmethod
    def post(self):

        arguments = arguments_parser.parse_args()
        fresh_user = User(username=arguments['username'], password=arguments['password'])
        fresh_user.make_hash()

        try:
            fresh_user.store()
            return {'message': f'User {fresh_user.username} stored'}
        except IntegrityError:
            return {'message': f'User {fresh_user.username} already exist'}, 202


# define a class for user login
class LogUser(Resource):

    def post(self):

        arguments = arguments_parser.parse_args()
        if not User.query.filter_by(username=arguments['username']).first():

            return {'message': 'No such user. Login again'}

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

    @jwt_required
    def get(self):
        users_json = [{'username': user.username, 'password': user.password} for user in User.query.all()]
        # print(get_raw_jwt())
        return {'users': users_json}

    @staticmethod
    def delete():
        User.del_all_users()

        return {'message': 'All users in the database have been deleted'}
