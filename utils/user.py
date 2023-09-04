from flask import g
from ..models import UserModel


# Function to return the current user
def get_user():
    aid = g.get("aid")
    return UserModel.query.filter(UserModel.auth_id == aid).first()
