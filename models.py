from .app import db 
from sqlalchemy.dialects.postgresql import JSON, BIGINT
from tsidpy import TSID
from sqlalchemy import text

class UserModel(db.Model):
    __tablename__ = 'users'

    uid = db.Column(BIGINT, primary_key=True, default=TSID.create().number)
    auth_id = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(32), index=True, unique=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    access_level = db.Column(db.Integer, default=0)
    email = db.Column(db.String(), nullable=True)

    def __init__(self, auth_id, username, first_name, last_name, email, access_level=0):
        self.auth_id = auth_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.access_level = access_level
        self.email = email
    
    def __repr__(self):
        return f"<User {self.username}"
    

class ProjectModel(db.Model):
    __tablename__='projects'

    pid = db.Column(BIGINT, primary_key=True, default=TSID.create().number)
    created_by = db.Column(BIGINT, db.ForeignKey('users.uid'))
    name = db.Column(db.String(32), index=True, unique=True)
    description = db.Column(db.String())
    date_created = db.Column(db.DateTime(), server_default=text('NOW()'))
    billing_address = db.Column(db.String(), nullable=True)
    billing_secondary_address = db.Column(db.String(), nullable=True)
    billing_city = db.Column(db.String(), nullable=True)
    billing_state = db.Column(db.String(), nullable=True)
    billing_zip = db.Column(db.String(), nullable=True)
    billing_country = db.Column(db.String(), nullable=True)
    billing_phone = db.Column(db.String(), nullable=True)
    billing_email = db.Column(db.String(), nullable=True)
    destination_email = db.Column(db.String(), nullable=True)


    def __init__(self, created_by, name, description, date_created, billing_address, billing_secondary_address, billing_city, billing_state, billing_zip, billing_country, billing_phone, billing_email, destination_email):
        self.created_by = created_by
        self.name = name
        self.description = description
        self.date_created = date_created
        self.billing_address = billing_address
        self.billing_secondary_address = billing_secondary_address
        self.billing_city = billing_city
        self.billing_state = billing_state
        self.billing_zip = billing_zip
        self.billing_country = billing_country
        self.billing_phone = billing_phone
        self.billing_email = billing_email
        self.destination_email = destination_email


class SharedWithModel(db.Model):
    __tablename__='shared_with'
    uid = db.Column(BIGINT, db.ForeignKey('users.uid'), primary_key=True)
    pid = db.Column(BIGINT, db.ForeignKey('projects.pid'), primary_key=True)
    payrate = db.Column(db.Float, default=0.0, nullable=True)
    upper_limit = db.Column(db.Float, default=0.0, nullable=True)

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