from database.db import db
import uuid

class User(db.Model):
    """Model representing a job seeker or user of the system.
    
    This model stores information about the job seeker using the system, including their
    personal details, work experience, and job search preferences.
    
    Attributes:
        id (str): Primary key, UUID string
        name (str): Full name of the job seeker
        email (str): Unique email address of the job seeker
        company (str): Name of the job seeker's current or previous company
        title (str): Job seeker's current or target job title
        industry (str): Industry sector of interest
        preferences (dict): JSON field storing user preferences including target companies,
                           job types, locations, years of experience, skills, and job level
    
    Relationships:
        - Has many Sessions (one-to-many relationship)
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    company = db.Column(db.String(100))
    title = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    preferences = db.Column(db.JSON)

    sessions = db.relationship("Session", backref="user", lazy=True)

class Session(db.Model):
    """Model representing a chat session between a user and the AI assistant.
    
    This model manages the conversation context and maintains the relationship between
    messages and sequence steps within a single chat session.
    
    Attributes:
        id (str): Primary key, UUID string
        user_id (str): Foreign key linking to the User model
        created_at (datetime): Timestamp when the session was created
        session_title (str): Title/name of the chat session
    
    Relationships:
        - Belongs to a User (many-to-one relationship)
        - Has many Messages (one-to-many relationship)
        - Has many SequenceSteps (one-to-many relationship)
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    session_title = db.Column(db.String(100), default="New Session")

    messages = db.relationship("Message", backref="session", lazy=True, cascade="all, delete-orphan")
    steps = db.relationship("SequenceStep", backref="session", lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    """Model representing a single message in a chat session.
    
    This model stores individual messages exchanged between the user and the AI assistant
    within a chat session, maintaining the conversation history.
    
    Attributes:
        id (str): Primary key, UUID string
        session_id (str): Foreign key linking to the Session model
        sender (str): Identifier of who sent the message ("user" or "ai")
        content (str): The actual message content
        timestamp (datetime): When the message was sent
    
    Relationships:
        - Belongs to a Session (many-to-one relationship)
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("session.id"))
    sender = db.Column(db.String(10))  # "user" or "ai"
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class SequenceStep(db.Model):
    """Model representing a single step in a candidate outreach sequence.
    
    This model stores the content and order of each step in a recruitment outreach sequence.
    Each step is associated with a specific chat session and has a unique identifier.
    
    Attributes:
        id (str): Primary key, UUID string
        session_id (str): Foreign key linking to the Session model
        step_number (int): The order of this step in the sequence
        content (str): The actual content/text of the outreach step
    
    Relationships:
        - Belongs to a Session (many-to-one relationship)
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("session.id"))
    step_number = db.Column(db.Integer)
    content = db.Column(db.Text)
