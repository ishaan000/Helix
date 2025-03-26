import unittest
from app import create_app
from database.db import db
from database.models import User, Session, Message, SequenceStep

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_db_insert_flow(self):
        with self.app.app_context():
            user = User(name="Ishaan", company="SellScale", preferences={"tone": "casual"})
            db.session.add(user)
            db.session.commit()

            session = Session(user_id=user.id)
            db.session.add(session)
            db.session.commit()

            msg = Message(session_id=session.id, sender="user", content="Looking for a React dev")
            db.session.add(msg)

            step = SequenceStep(session_id=session.id, step_number=1, content="Hi, I saw your profile...")
            db.session.add(step)

            db.session.commit()

            self.assertEqual(User.query.count(), 1)
            self.assertEqual(Session.query.count(), 1)
            self.assertEqual(Message.query.count(), 1)
            self.assertEqual(SequenceStep.query.count(), 1)

if __name__ == "__main__":
    unittest.main()
