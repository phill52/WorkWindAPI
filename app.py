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

@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if request.is_json:
            data=request.get_json()
            print("Data is here " , )
            new_username=data[0]['username'].lower()
            existing_user = UserModel.query.filter_by(username=new_username).first()
            print(existing_user)
            if existing_user is not None:
                return jsonify({"error": "User already exists"}), 409
            new_user=UserModel(auth_id=data[0]['auth_id'], username=data[0]['username'],
                               first_name=data[0]['first_name'], last_name=data[0]['last_name'],
                               email=data[0]['email'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "Successfully created"}, {
                "uid" : new_user.uid,
                "auth_id": new_user.auth_id,
                "username": new_user.username,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email
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

@app.route('/users/<id>', methods=['GET' 'PATCH', 'DELETE'])
def get_users_by_id(id):
    if request.method == 'GET':
        print(id)
        user=UserModel.query.filter(UserModel.uid == id).first()
        if user is None:
            return jsonify({"error": "User Not found"}), 404
        else:
            return jsonify({"uid":user.uid,
                            "auth_id": user.auth_id,
                            "username": user.username})
    elif request.method == 'PATCH':
        data = request.get_json()
        user_id = data['uid']
        username = data['username'].lower()
        authid = data['auth_id']
        existing_user = UserModel.query.filter_by(uid=user_id).first()
        if existing_user is not None:
            return jsonify({"error": "User already exists"}), 409
        new_user = UserModel(username=data['username'], auth_id=data['auth_id'])
        db.session.add(new_user)
        db.session.commit()
        return "Update success ", jsonify({
            "uid": new_user.uid,
            "auth_id": new_user.auth_id,
            "username": new_user.username
        })
    else:
        return jsonify({"error": "The request is not JSON format"}),400


# @app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
# def handle_userid(user_id):
#     if request.method == 'GET':
#         user=UserModel.query.filter(UserModel.uid==user_id).first()
#         if user is None:
#             return jsonify({"error": "User not found"}), 404
#         else: 
#             return jsonify({
#                 "uid": user.uid,
#                 "auth_id": user.auth_id,
#                 "username": user.username
#             })
#     elif request.method == 'PUT':
#         user=UserModel.query.get(user_id)
#         if user is None:
#             return jsonify({"error": "User not found"}), 404
#         else:
#             data=request.get_json()
#             user.username=data['username']
#             db.session.commit()
#             return jsonify({
#                 "uid": user.uid,
#                 "auth_id": user.auth_id,
#                 "username": user.username
#             })
#     elif request.method == 'DELETE' :
#         user=UserModel.query.get(user_id)
#         if user is None:
#             return jsonify({"error": "User not found"}), 404
#         else:
#             db.session.delete(user)
#             db.session.commit()
#             return jsonify({"message": "User deleted successfully"}), 200



if __name__ == '__main__':
    app.run(debug=True)