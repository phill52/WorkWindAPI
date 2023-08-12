from flask import Blueprint
from utils.user import get_user

project_bp = Blueprint("project", __name__)

@project_bp.route("/project", methods=["POST"])
def project():
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "The request payload is not in JSON format"}), 400
        data = request.get_json()
        name = data["name"]
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
                "pid": new_project.pid,
                "name": new_project.name,
                "created_by": new_project.created_by,
            }
        )

@project_bp.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
def handle_projectid(project_id):
    project_id = project_id
    # Could use ProjectModel.query.get_or_404(project_id) instead
    if (project := ProjectModel.query.get(project_id)) is None:
        return jsonify({"error": "Project not found"}), 404
    elif request.method == "GET":
        return jsonify(
            {"pid": project.pid, "name": project.name, "created_by": project.created_by}
        )
    elif request.method == "PUT":
        data = request.get_json()
        project.name = data["name"]
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