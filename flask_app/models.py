from flask_app import db
from flask import current_app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    lname = db.Column(db.String(120))
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name, lname, email, username, password):
        self.name = name
        self.lname = lname
        self.email = email
        self.username = username
        self.password = password


