import unittest
from unittest.mock import patch
from app import create_app
from database.db import db
from database.models import Message

class ChatEndpointTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    @patch("app.chat_with_openai")
    def test_chat_endpoint_creates_messages(self, mock_openai_chat):
        mock_openai_chat.return_value = "Sure, here's a great outreach message."

        payload = {
            "message": "Looking for a backend engineer in NYC",
            "session_id": 42
        }

        response = self.client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("response", data)
        self.assertIn("outreach message", data["response"])

        with self.app.app_context():
            messages = Message.query.filter_by(session_id=42).all()
            self.assertEqual(len(messages), 2)  # user + AI

if __name__ == "__main__":
    unittest.main()
