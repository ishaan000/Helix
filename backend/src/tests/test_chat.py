import unittest
from unittest.mock import patch
from app import create_app
from database.db import db
from database.models import Message, SequenceStep

class ChatEndpointTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_tool_call_and_sequence_generation(self):
        session_id = 99
        message = "Generate a 3-step outreach sequence for a Product Manager in SF"

        res = self.client.post("/chat", json={"message": message, "session_id": session_id})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("response", data)
        
        # Check if response contains sequence content
        response_text = data["response"]
        self.assertIn("3-step outreach sequence", response_text)
        self.assertIn("Step 1:", response_text)
        self.assertIn("Step 2:", response_text)
        self.assertIn("Step 3:", response_text)

        with self.app.app_context():
            steps = SequenceStep.query.filter_by(session_id=session_id).all()
            self.assertEqual(len(steps), 3)
            for step in steps:
                self.assertIsNotNone(step.content)

    def test_sequence_endpoint(self):
        # First generate a sequence
        session_id = 100
        message = "Create a sequence for a Senior Engineer in New York"
        self.client.post("/chat", json={"message": message, "session_id": session_id})

        # Then test the sequence endpoint
        res = self.client.get(f"/sequence/{session_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check sequence structure
        for step in data:
            self.assertIn("step_number", step)
            self.assertIn("content", step)
            self.assertIsInstance(step["step_number"], int)
            self.assertIsInstance(step["content"], str)

    def test_chat_without_location(self):
        session_id = 101
        message = "Generate a sequence for a UX Designer"
        
        res = self.client.post("/chat", json={"message": message, "session_id": session_id})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("response", data)
        # Should ask for location
        self.assertIn("location", data["response"].lower())

if __name__ == "__main__":
    unittest.main()
