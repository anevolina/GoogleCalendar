import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from os.path import join, dirname

app = Flask(__name__)
api = Api(app)

dotenv_path = join(dirname('__file__'), '.env')
load_dotenv(dotenv_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')

db = SQLAlchemy(app)

import views, resources, models

@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')