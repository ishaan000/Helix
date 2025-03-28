from database.db import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    company = db.Column(db.String(100))
    title = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    preferences = db.Column(db.JSON)

    sessions = db.relationship("Session", backref="user", lazy=True)

class Session(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    session_title = db.Column(db.String(100), default="New Session")

    messages = db.relationship("Message", backref="session", lazy=True, cascade="all, delete-orphan")
    steps = db.relationship("SequenceStep", backref="session", lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("session.id"))
    sender = db.Column(db.String(10))  # "user" or "ai"
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class SequenceStep(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("session.id"))
    step_number = db.Column(db.Integer)
    content = db.Column(db.Text)
