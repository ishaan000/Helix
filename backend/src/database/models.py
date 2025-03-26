from database.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    preferences = db.Column(db.JSON)  # you can keep things like tone, job type, etc.

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    sender = db.Column(db.String(10))  # "user" or "ai"
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class SequenceStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    step_number = db.Column(db.Integer)
    content = db.Column(db.Text)
