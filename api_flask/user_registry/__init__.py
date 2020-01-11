import os
import shelve

from flask import Flask, g
from flask_restful import Resource, reqparse, Api


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument(name='username', help='This field cannot be blank', required=True)
parser.add_argument(name='password', help='This field cannot be blank', required=True)

def get_db():
    db = getattr(g, '_databese', None)
    if db is None:
        db = g._database = shelve.open('devices.db')
    return db


class UserRegistration(Resource):
    def post(self):
        args = parser.parse_args()
        return args

class UserLogin(Resource):
    def post(self):
        return {'message': 'User login'}


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
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }


api.add_resource(UserRegistration, '/registration')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogoutAccess, '/logout/access')
api.add_resource(UserLogoutRefresh, '/logout/refresh')
api.add_resource(TokenRefresh, '/token/refresh')
api.add_resource(AllUsers, '/users')
api.add_resource(SecretResource, '/secret')