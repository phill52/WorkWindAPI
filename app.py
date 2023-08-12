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

from endpoints.project import project_bp

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
def users():
    if request.method == "GET":
        return jsonify(
            {"uid": user.uid, "auth_id": user.auth_id, "username": user.username}
            for user in UserModel.query.all()
        )
    elif request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
        data = request.get_json()
        username = cleaner.clean(data["username"])
        if (UserModel.query.filter_by(username=username.lower()).first()) is not None:
            return jsonify({"error": "User already exists"}), 409
        new_user = UserModel(auth_id=data["auth_id"], username=username)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(
            {
                "uid": new_user.uid,
                "auth_id": new_user.auth_id,
                "username": new_user.username,
            }
        )


@app.route("/auth/users", methods=["GET"])
@require_auth()
def handle_authid():
    if request.method == "GET":
        aid = g.get("aid")
        print("this aids", aid)
        user = UserModel.query.filter(UserModel.auth_id == aid).first()
        if user is None:
            return jsonify({"data": False})
        else:
            return jsonify({"data": user})


@app.route("/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def handle_userid(user_id):
    if request.method == "GET":
        user = UserModel.query.filter(UserModel.uid == user_id).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            return jsonify(
                {"uid": user.uid, "auth_id": user.auth_id, "username": user.username}
            )
    elif request.method == "PUT":
        user = UserModel.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            data = request.get_json()
            user.username = data["username"]
            db.session.commit()
            return jsonify(
                {"uid": user.uid, "auth_id": user.auth_id, "username": user.username}
            )
    elif request.method == "DELETE":
        user = UserModel.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
