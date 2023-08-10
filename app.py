from flask import Flask,  jsonify, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config, DevelopmentConfig, ProductionConfig, StagingConfig, TestingConfig
import os
from .validator import Auth0JWTBearerTokenValidator
from authlib.integrations.flask_oauth2 import ResourceProtector
from flask_cors import CORS

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_IDENTIFIER = os.environ.get("API_IDENTIFIER")
SECRET = os.environ.get("AUTH0_SECRET")
ALGORITHM = os.environ.get("ALGORITHM")

require_auth  = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    AUTH0_DOMAIN,
    API_IDENTIFIER
)
require_auth.register_token_validator(validator)


app=Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


from .models import *
migrate = Migrate(app, db)
CORS(app)

# Function to return the current user
@require_auth()
def get_user():
    aid = g.get('aid')
    return user if (user := UserModel.query.filter(UserModel.auth_id == aid).first()) is not None else False

@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if request.is_json:
            data=request.get_json()
            username=data['username'].lower()
            existing_user = UserModel.query.filter_by(username=username).first()
            if existing_user is not None:
                return jsonify({"error": "User already exists"}), 409
            aid = request.aid
            new_user=UserModel(auth_id=data['auth_id'], username=data['username'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                "uid" : new_user.uid,
                "auth_id": new_user.auth_id,
                "username": new_user.username
            })
        else: 
            return jsonify({"error": "The request payload is not in JSON format"}),400
    elif request.method == 'GET':
        users=UserModel.query.all()
        results=[
            {
                "uid": user.uid,
                "auth_id": user.auth_id,
                "username": user.username
            } for user in users]
        return jsonify(results)

@app.route('/auth/users', methods=['GET'])
@require_auth()
def handle_authid():
    if request.method == 'GET':
        aid = g.get('aid') 
        print("this aids", aid)
        user=UserModel.query.filter(UserModel.auth_id==aid).first()
        if user is None:
            return jsonify({"data":False})
        else:
            return jsonify({"data": user})



@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_userid(user_id):
    if request.method == 'GET':
        user=UserModel.query.filter(UserModel.uid==user_id).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else: 
            return jsonify({
                "uid": user.uid,
                "auth_id": user.auth_id,
                "username": user.username
            })
    elif request.method == 'PUT':
        user=UserModel.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            data=request.get_json()
            user.username=data['username']
            db.session.commit()
            return jsonify({
                "uid": user.uid,
                "auth_id": user.auth_id,
                "username": user.username
            })
    elif request.method == 'DELETE' :
        user=UserModel.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 200

# Project routes

@app.route('/project', methods=['POST'])
@require_auth()
def project():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}),400
        data = request.get_json()
        name = data['name']
        if not (user := get_user()):
            return jsonify({"error": "Could not identify user"}),400
        if ProjectModel.query.filter_by(name=name, user_id=user.uid).first() is not None:
            return jsonify({"error": "Project already exists"}), 409
        new_project = ProjectModel(name = name, created_by = user.uid)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({
            "pid": new_project.pid,
            "name": new_project.name,
            "created_by": new_project.created_by
        })


if __name__ == '__main__':
    app.run(debug=True)