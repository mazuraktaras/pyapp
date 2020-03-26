from flask_restful import Resource, reqparse
from .models import Users

# Instantiate the argument's parser
arguments_parser = reqparse.RequestParser()

# Add arguments for parsing
arguments_parser.add_argument('username', required=True, help='Can not be blank')
arguments_parser.add_argument('password', required=True, help='Can not be blank')


# define a class for user registration
class RegUser(Resource):

    def post(self):

        arguments = arguments_parser.parse_args()
        fresh_user = Users(username=arguments['username'], password=arguments['password'])
        try:
            fresh_user.store()
            return {'message': f'User {fresh_user.username} stored'}

        except:

            return {'message': f'User {fresh_user.username} exist'}, 501


# define a class for user login
class LogUser(Resource):

    def post(self):

        arguments = arguments_parser.parse_args()
        if not Users.query.filter_by(username=arguments['username']).first():

            return {'message': 'No such user. Login again'}
        else:
            user = Users.query.filter_by(username=arguments['username']).first()
            if arguments['password'] == user.password:

                return {'message': 'Successfully logged'}
            else:
                return {'message': 'Bad password'}


# define a class for user logout
class LogoutUser(Resource):
    def post(self):
        return {'message': 'Logout'}


# define a class for all users actions
class AllUsers(Resource):

    def get(self):
        users_json = [{'username': user.username, 'password': user.password} for user in Users.query.all()]

        return {'users': users_json}

    def delete(self):
        Users.del_all_users()

        return {'message': 'All users in database deleted'}
