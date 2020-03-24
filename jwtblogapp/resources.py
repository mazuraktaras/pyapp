from flask_restful import Resource, reqparse



# Instantiate the argument's parser
arg_parser = reqparse.RequestParser()

# Add arguments for parsing
arg_parser.add_argument('username', required=True, help='Can not be blank')
arg_parser.add_argument('password', required=True, help='Can not be blank')

# define a class for user registration
class RegUser(Resource):
    def post(self):
        return arg_parser.parse_args()


# define a class for user login
class LogUser(Resource):
    def post(self):
        return {'message': 'Login'}

# define a class for user logout
class LogoutUser(Resource):
    def post(self):
        return {'message': 'Logout'}