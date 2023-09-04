import json
from flask import Flask, jsonify, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    StagingConfig,
    TestingConfig,
)
import os
from .validator import Auth0JWTBearerTokenValidator
from authlib.integrations.flask_oauth2 import ResourceProtector
from flask_cors import CORS
from bleach.sanitizer import Cleaner

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_IDENTIFIER = os.environ.get("API_IDENTIFIER")
SECRET = os.environ.get("AUTH0_SECRET")
ALGORITHM = os.environ.get("ALGORITHM")

require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(AUTH0_DOMAIN, API_IDENTIFIER)
require_auth.register_token_validator(validator)


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

from .endpoints.project import project_bp

app.register_blueprint(project_bp)


from .models import *

migrate = Migrate(app, db)
CORS(app)


# Creating a Bleach sanitizer cleaner instance
cleaner = Cleaner()


@app.route("/")
def index():
    return jsonify({"message": "Hello, World!"})


@app.route("/users", methods=["GET", "POST"])
@require_auth()
def users():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            dumped_data = json.dumps(data)

            if "username" not in dumped_data:
                return jsonify({"error": "Username is not found"}), 400

            if "first_name" not in dumped_data:
                return jsonify({"error": "First Name is not found"}), 400

            if "last_name" not in dumped_data:
                return jsonify({"error": "Last Name is not found"}), 400

            elif type(data["username"]) != str:
                return (
                    jsonify({"error": "Update failed username is not of type string"}),
                    400,
                )
            elif type(data["first_name"]) != str:
                return (jsonify({"error": "First name is not of type string"}), 400)
            elif type(data["last_name"]) != str:
                return (jsonify({"error": "Last name is not of type string"}), 400)

            else:
                # username=data['username'].lower()
                aid = g.get("aid")
                curr_email = g.get("email")
                print("This aid is", aid)
                print("Current email is", curr_email)
                current_user_auth_id = UserModel.query.filter(
                    UserModel.auth_id == aid
                ).first()
                current_user_username = UserModel.query.filter(
                    UserModel.username == data["username"]
                ).first()
                if current_user_auth_id is not None:
                    return jsonify(
                        [
                            {
                                "error": "An account with that auth_id alreay exists",
                                "data": [
                                    {
                                        "username": current_user_auth_id.username,
                                        "first_name": current_user_auth_id.first_name,
                                        "last_name": current_user_auth_id.last_name,
                                        "email": curr_email,
                                    },
                                    409,
                                ],
                            }
                        ]
                    )
                if current_user_username is not None:
                    return (
                        jsonify(
                            {"error": "An account with that username already exists"}
                        ),
                        400,
                    )
                else:
                    # aid = request.aid
                    new_user = UserModel(
                        auth_id=aid,
                        username=data["username"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        email=curr_email,
                    )
                    new_username = new_user.username
                    if new_user is None:
                        return jsonify({"error": "User not found"}), 404
                    # elif type(new_username) != str:
                    #     return (
                    #         jsonify(
                    #             {
                    #                 "error": "Update failed username is not of type string"
                    #             }
                    #         ),
                    #         400,
                    #     )
                    else:
                        new_username_length = len(new_username)
                        if new_username_length < 4 or new_username_length > 32:
                            return (
                                jsonify(
                                    {
                                        "error": "Update failed username length has to be in between 4-32 characters"
                                    }
                                ),
                                400,
                            )
                        elif new_username.isalnum() == False:
                            return (
                                jsonify(
                                    {
                                        "error": "Update failed username must be alphanumeric characters [A-Z] and [0-9]"
                                    }
                                ),
                                400,
                            )
                        else:
                            db.session.add(new_user)
                            db.session.commit()
                            return jsonify(
                                [
                                    {"message": "Successfully created"},
                                    {
                                        # "uid" : new_user.uid,
                                        "auth_id": new_user.auth_id,
                                        "username": new_user.username,
                                        "first_name": new_user.first_name,
                                        "last_name": new_user.last_name,
                                        "email": new_user.email,
                                    },
                                ]
                            )
        else:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
    elif request.method == "GET":
        users = UserModel.query.all()
        results = [
            {"uid": user.uid, "auth_id": user.auth_id, "username": user.username}
            for user in users
        ]
        return jsonify(results)


@app.route("/auth/users", methods=["GET"])
@require_auth()
def handle_authid():
    if request.method == "GET":
        aid = g.get("aid")
        print("this aids", aid)
        user = UserModel.query.filter(UserModel.auth_id == aid).first()
        print(g.get("email"))
        if user is None:
            return jsonify({"data": False})
        else:
            return jsonify(
                {
                    "data": {
                        column.name: getattr(user, column.name)
                        for column in user.__table__.columns
                    }
                }
            )


@app.route("/users/<user_id>", methods=["GET", "PATCH", "DELETE"])
@require_auth()
def handle_userid(user_id):
    if request.method == "GET":
        a_id = g.get("aid")
        user = UserModel.query.filter(
            UserModel.uid == user_id and UserModel.auth_id == a_id
        ).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            return jsonify(
                {
                    "uid": user.uid,
                    "auth_id": user.auth_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            )
    elif request.method == "PATCH":
        a_id = g.get("aid")
        data = request.get_json()
        user = UserModel.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        if user.auth_id != a_id:
            return (
                jsonify({"error": "A user can't update another user's information"}),
                403,
            )
        else:
            dumped_data = json.dumps(data)
            if "username" in dumped_data:
                if type(data["username"]) != str:
                    return (
                        jsonify(
                            {"error": "Update failed username is not of type string"}
                        ),
                        400,
                    )
                username_len = len(data["username"])
                if username_len < 4 or username_len > 32:
                    return (
                        jsonify(
                            {
                                "error": "Update failed username length has to be in between 4-32 characters"
                            }
                        ),
                        400,
                    )
                else:
                    if data["username"].isalnum() == False:
                        return (
                            jsonify(
                                {
                                    "error": "Update failed username must be alphanumeric characters [A-Z] and [0-9]"
                                }
                            ),
                            400,
                        )

                    else:
                        user.username = data["username"]
            if "first_name" in dumped_data:
                if type(data["first_name"]) != str:
                    return (
                        jsonify(
                            {"error": "Update failed first_name is not of type string"}
                        ),
                        400,
                    )
                else:
                    user.first_name = data["first_name"]
            if "last_name" in dumped_data:
                if type(data["last_name"]) != str:
                    return (
                        jsonify(
                            {"error": "Update failed last_name is not of type string"}
                        ),
                        400,
                    )
                else:
                    user.last_name = data["last_name"]
            if "email" in dumped_data:
                if type(data["email"]) != str:
                    return (
                        jsonify({"error": "Update failed email is not of type string"}),
                        400,
                    )
                else:
                    user.email = data["email"]

            user.verified = True
            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Update successful",
                    "uid": user.uid,
                    "auth_id": user.auth_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            )

    elif request.method == "DELETE":
        user = UserModel.query.get(user_id)
        a_id = g.get("aid")
        if user is None:
            return jsonify({"error": "User not found"}), 404
        elif user.auth_id != a_id:
            return (
                jsonify({"error": "A user cannot delete another person's account"}),
                403,
            )

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


if __name__ == "__main__":
    app.run(debug=True)
