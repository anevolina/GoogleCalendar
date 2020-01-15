from flask import Flask
from flask_restful import Resource, reqparse, Api

from models import UserModel


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument(name='username', help='This field cannot be blank', required=True)
parser.add_argument(name='password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        args = parser.parse_args()

        username = args['username']
        password = UserModel.generate_hash(args['password'])

        if UserModel.find_by_username(username):
            return {'message': 'User {} already exists'.format(username)}

        new_user = UserModel(
            username = username,
            password = password
        )

        try:
            new_user.save_to_db()
            return {
                'message': 'User {} was created'.format(username)
            }
        except:
            return {'message': 'Something went wrong'}, 500

        return args

class UserLogin(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']

        current_user = UserModel.find_by_username(username)

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(username)}

        if UserModel.verify_password(password, current_user.password):
            return {'message': 'Logged in as {}'.format(username)}

        else:
            return {'message': 'Wrong password'}



class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refreshed'}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }