from flask import Blueprint, request, jsonify
from ..utils.user import get_user
from ..utils.validation import *
from datetime import datetime
from ..models import db, ProjectModel, UserModel, SharedWithModel
import os
from ..validator import Auth0JWTBearerTokenValidator
from authlib.integrations.flask_oauth2 import ResourceProtector

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_IDENTIFIER = os.environ.get("API_IDENTIFIER")

require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(AUTH0_DOMAIN, API_IDENTIFIER)
require_auth.register_token_validator(validator)

project_bp = Blueprint("project", __name__)

# Dictionary to map column names to validation functions
column_check_map = {
    "name": check_project_name,
    "description": check_project_description,
    "billing_address": check_address,
    "billing_second_address": check_address,
    "billing_city": check_city,
    "billing_state": check_state,
    "billing_zip": check_zip,
    "billing_country": check_country,
    "billing_phone": check_phone,
    "billing_email": check_email,
    "destination_email": check_email,
}


def check_creator(project):
    error, error_code = None, None
    if not (user := get_user()):
        error = "Could not identify user"
        error_code = 400
    elif project.created_by != user.uid:
        error = "User is not the creator of this project"
        error_code = 403
    return error, error_code


@project_bp.route("/project", methods=["POST"])
@require_auth()
def project():
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
        data = request.get_json()
        new_project = ProjectModel()
        for data_key in data.keys():
            if data_key in new_project.__table__.columns:
                try:
                    data_value = column_check_map[data_key](data[data_key])
                    new_project.__setitem__(data_key, data_value)
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
                except KeyError:
                    pass
        if new_project.name is None:
            return jsonify({"error": "Project name is required"}), 400
        if not (user := get_user()):
            return jsonify({"error": "Could not identify user"}), 400
        if (
            ProjectModel.query.filter_by(
                name=new_project.name, created_by=user.uid
            ).first()
            is not None
        ):
            return jsonify({"error": "Project already exists"}), 409
        new_project.__setitem__("created_by", user.uid)
        new_project.__setitem__("date_created", datetime.now())
        db.session.add(new_project)
        db.session.commit()
        return jsonify(
            {
                column.name: new_project.__getitem__(column.name)
                for column in new_project.__table__.columns
            }
        )


@project_bp.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
@require_auth()
def handle_projectid(project_id):
    # Could use ProjectModel.query.get_or_404(project_id) instead
    if (project := ProjectModel.query.get(project_id)) is None:
        return jsonify({"error": "Project not found"}), 404
    elif request.method == "GET":
        return jsonify(
            {
                column.name: project.__getitem__(column.name)
                for column in project.__table__.columns
            }
        )
    elif request.method == "PUT":
        data = request.get_json()
        if (error, error_code := check_creator(project)) is not None:
            return jsonify({"error": error}), error_code
        for data_key in data.keys():
            if data_key in project.__table__.columns:
                try:
                    data_value = column_check_map[data_key](data[data_key])
                    project.__setitem__(data_key, data_value)
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
                except KeyError:
                    pass
        db.session.commit()
        return jsonify(
            {
                column.name: new_project.__getitem__(column.name)
                for column in new_project.__table__.columns
            }
        )
    elif request.method == "DELETE":
        if (error, error_code := check_creator(project)) is not None:
            return jsonify({"error": error}), error_code
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200


@project_bp.route("/project/share/<project_id>", methods=["POST"])
@require_auth()
def share_project(project_id):
    if (project := ProjectModel.query.get(project_id)) is None:
        return jsonify({"error": "Project not found"}), 404
    elif request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
        data = request.get_json()
        username = data["username"]
        if not (user := UserModel.query.filter_by(username=username).first()):
            return jsonify({"error": "User not found"}), 404
        new_share = SharedWithModel(uid=user.uid, pid=project_id)
        db.session.add(new_share)
        db.session.commit()
        return jsonify(
            {
                column.name: new_project.__getitem__(column.name)
                for column in new_project.__table__.columns
            }
        )
