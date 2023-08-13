import json
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
            data = request.get_json()
            #new_username=data[0]['username'].lower()
            aid = g.get('aid')
            print("A_id is", aid)
            # existing_user = UserModel.query.filter_by(username=new_username).first()
            existing_user = UserModel.query.filter(UserModel.auth_id==aid).first()
            # if existing_user is not None:
            #     return jsonify({"error": "User already exists"}), 409
            new_user=UserModel(auth_id=aid, username=data[0]['username'], first_name=data[0]['first_name'],
                            last_name=data[0]['last_name'], email=data[0]['email'])
            new_username = new_user.username
            if new_user is None:
                return jsonify({"error": "User does not exist"}), 404
            elif type(new_username) != str:
                return jsonify({"error": "Update failed username is not of type string"}), 409
            else:
                new_username_length = len(new_username)
                if new_username_length < 4 or new_username_length > 32:
                    return jsonify({"error": "Update failed username length has to be in between 4-32 characters"}), 409
                elif new_username.isalnum() == False:
                    return jsonify({"error": "Update failed username must be alphanumeric characters [A-Z] and [0-9]"}), 409
                else:
                    db.session.add(new_user)
                    db.session.commit()
                    return jsonify({"message": "Successfully created"}, {
                        # "uid" : new_user.uid,
                        "auth_id": new_user.auth_id,
                        "username" : new_user.username,
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

@app.route('/users/<user_id>', methods=['GET', 'PATCH', 'DELETE'])
def request_users_by_id(user_id):
        if request.method == 'GET':
            print(user_id)
            a_id = g.get('aid')
            print("this a_id", a_id)
            user=UserModel.query.filter(UserModel.uid == user_id and UserModel.auth_id == a_id).first()
            if user is None:
                return jsonify({"error": "User Not found"}), 404
            else:
                return jsonify({
                    "uid":user.uid,
                    "auth_id": user.auth_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                })
        elif request.method == 'PATCH':
            data = request.get_json()

            user = UserModel.query.filter(UserModel.uid == user_id).one_or_none()

            if user is None:
                return jsonify({"error": "User does not exist"}), 404
            
            if 'username' in data:
                user.username = request.form['username']
                print("Update username", user.username)
            elif 'first_name' in data:
                user.first_name = request.form['first_name']
            elif 'last_name' in data:
                user.last_name = request.form['last_name']
            elif 'email' in data:
                user.email = request.form['email']

            user.verified = True
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Update successful',
                "uid":user.uid,
                    "auth_id": user.auth_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
            })

        elif request.method == 'DELETE':
            user=UserModel.query.get(user_id)

            if user is None:
                return jsonify({"error": "User is not found"}), 404
            else:
                db.session.delete(user)
                db.session.commit()
                return jsonify({"message": "User deleted successfully"}), 200




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