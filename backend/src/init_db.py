from app import create_app
from database.db import db
from database import models

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")
