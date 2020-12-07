from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    login = db.Column(db.String(1000), unique=True)
    email = db.Column(db.String(100), unique=True)
    md5_password = db.Column(db.String(100))
    TTL = db.Column(db.String(100))