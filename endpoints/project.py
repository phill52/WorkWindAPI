from flask import Blueprint
from utils.user import get_user
from utils.validation import *

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


@project_bp.route("/project", methods=["POST"])
def project():
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
        data = request.get_json()
        name = data["name"]
        try:
            name = check_project_name(data["name"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        if not (user := get_user()):
            return jsonify({"error": "Could not identify user"}), 400
        if (
            ProjectModel.query.filter_by(name=name, user_id=user.uid).first()
            is not None
        ):
            return jsonify({"error": "Project already exists"}), 409
        new_project = ProjectModel(name=name, created_by=user.uid)
        db.session.add(new_project)
        db.session.commit()
        return jsonify(
            {
                column.name: getattr(new_project, column.name)
                for column in new_project.__table__.columns
            }
        )


@project_bp.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
def handle_projectid(project_id):
    # Could use ProjectModel.query.get_or_404(project_id) instead
    if (project := ProjectModel.query.get(project_id)) is None:
        return jsonify({"error": "Project not found"}), 404
    elif request.method == "GET":
        return jsonify(
            {
                column.name: getattr(project, column.name)
                for column in project.__table__.columns
            }
        )
    elif request.method == "PUT":
        data = request.get_json()
        for data_key in data.keys():
            if data_key in project.__table__.columns:
                try:
                    data_value = column_check_map[data_key](data[data_key])
                    project[data_key] = data_value
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
                except KeyError:
                    pass
        db.session.commit()
        return jsonify(
            {
                column.name: getattr(project, column.name)
                for column in project.__table__.columns
            }
        )
    elif request.method == "DELETE":
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200


@project_bp.route("/project/share/<project_id>", methods=["POST"])
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
                column.name: getattr(new_share, column.name)
                for column in new_share.__table__.columns
            }
        )
