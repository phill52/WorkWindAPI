from .app import db 
from sqlalchemy.dialects.postgresql import JSON, BIGINT
from tsidpy import TSID
from sqlalchemy import text

class UserModel(db.Model):
    __tablename__ = 'users'

    uid = db.Column(BIGINT, primary_key=True, default=TSID.create().number)
    auth_id = db.Column(db.Integer())
    username = db.Column(db.String(32), index=True, unique=True)

    def __init__(self, auth_id, username):
        self.auth_id = auth_id
        self.username = username
    
    def __repr__(self):
        return f"<User {self.username}"
    

class ProjectModel(db.Model):
    __tablename__='projects'

    pid = db.Column(BIGINT, primary_key=True, default=TSID.create().number)
    created_by = db.Column(BIGINT, db.ForeignKey('users.uid'))
    name = db.Column(db.String(32), index=True, unique=True)

    def __init__(self, created_by, name, description):
        self.created_by = created_by
        self.name = name
        self.description = description

class SharedWithModel(db.Model):
    __tablename__='shared_with'
    uid = db.Column(BIGINT, db.ForeignKey('users.uid'), primary_key=True)
    pid = db.Column(BIGINT, db.ForeignKey('projects.pid'), primary_key=True)

    def __init__(self, uid, pid):
        self.uid = uid
        self.pid = pid
    
class ShiftsModel(db.Model):
    __tablename__='shifts'
    sid = db.Column(BIGINT, primary_key=True, default=TSID.create().number)
    pid = db.Column(BIGINT, db.ForeignKey('projects.pid'))
    uid = db.Column(BIGINT, db.ForeignKey('users.uid'))
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime(), nullable=True)

    def __init__(self, pid, uid, start_time, end_time):
        self.pid = pid
        self.uid = uid
        self.start_time = start_time
        self.end_time = end_time