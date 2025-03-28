from flask import Flask
from flask_cors import CORS
from socketio_instance import socketio
from database.db import db
from database.models import User, Session, Message, SequenceStep
from services.openai_client import chat_with_openai
from flask import request, jsonify
from dotenv import load_dotenv
import os
import uuid
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_chat_title(message: str) -> str:
    """Generate a meaningful title for the chat based on the first message."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a title generator for chat sessions. Create a concise, descriptive title (max 30 chars) that captures the main topic or goal of the conversation. 
                    The title should be professional and specific to the task. For example:
                    - "UX Lead Offer Letter" for a request to write an offer letter
                    - "Senior Dev Outreach" for generating outreach sequences
                    - "Interview Thank You" for thank you notes
                    Be very concise and specific."""
                },
                {
                    "role": "user",
                    "content": f"Generate a title for this chat message: {message}"
                }
            ],
            temperature=0.7,
            max_tokens=10
        )
        title = response.choices[0].message.content.strip()
        # Ensure title isn't too long and remove quotes if present
        title = title.replace('"', '').replace("'", "")
        return title[:30]
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return "New Chat"

def create_app(testing=False):
    app = Flask(__name__)
    CORS(app)

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///helix.db")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Create database tables
    with app.app_context():
        db.create_all()

    @socketio.on("session_updated")
    def handle_session_update(data):
        """Handle session title updates from the client"""
        try:
            session_id = data.get("session_id")
            new_title = data.get("session_title")
            
            if not session_id or not new_title:
                return
            
            # Update the session in the database
            session = Session.query.get(session_id)
            if session:
                session.session_title = new_title
                db.session.commit()
                
                # Broadcast the update to all clients
                socketio.emit("session_updated", {
                    "session_id": session_id,
                    "session_title": new_title
                })
        except Exception as e:
            print(f"Error handling session update: {str(e)}")

    @app.route("/")
    def index():
        return "Helix backend running!"
    
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        user_message = data.get("message")
        session_id = data.get("session_id")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400

        print(f"Processing chat for session_id: {session_id}")  # Debug log

        # Verify session exists
        session = Session.query.get(session_id)
        if not session:
            print(f"Session not found: {session_id}")  # Debug log
            return jsonify({"error": "Session not found"}), 404

        try:
            # Save user message to DB
            user_msg = Message(session_id=session_id, sender="user", content=user_message)
            db.session.add(user_msg)
            db.session.commit()

            # If this is the first message, generate a title
            if len(Message.query.filter_by(session_id=session_id).all()) == 1:
                title = generate_chat_title(user_message)
                session.session_title = title
                db.session.commit()
                print(f"Generated title: {title}")  # Debug log
                # Emit title update via WebSocket
                socketio.emit("session_updated", {
                    "session_id": session_id,
                    "session_title": title
                })

            # Fetch full chat history for this session
            past_messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()

            messages = [
                {
                    "role": "system",
                    "content": """
                            You are Helix, an AI recruiting assistant that helps users generate and refine personalized candidate outreach sequences.

                            **Rules to Follow:**

                            1. **Tool Usage**: Always use tools for sequence-related tasks. Never write or suggest sequence content directly.
                            - Available tools:
                                - `generate_sequence` (requires role and location)
                                - `revise_step` (requires step number and revision instruction)
                                - `change_tone` (requires tone and session_id)
                                - `add_step` (requires step content and session_id)
                                
                                - `generate_recruiting_asset`: Use this for one-off requests like "write an offer letter," "thank you note," or "follow-up email." This tool handles any recruiting-related task from natural language instructions.

                            2. **Clarify Intent**: If the user's request is unclear, ask a clarifying question before proceeding.

                            3. **Conversational Responses**: Respond conversationally if the user's input is vague or unrelated to sequence manipulation.

                            **Tone Guidance**:
                            - Technical roles → professional & direct
                            - Creative roles → casual & expressive
                            - Senior roles → formal & strategic
                            - Startup roles → energetic & conversational
                            - Enterprise roles → formal & structured

                            **Your Role**: Act as a friendly, smart recruiting co-pilot, not a chatbot.

                            **Before Responding**:
                            - Verify that your response complies with all rules above.
                            - Ensure you are using tools appropriately (if required).
                            - Avoid direct content creation or unnecessary tool usage.
                            If not compliant, revise your response before sending it.
    """
                }
            ]           
            for msg in past_messages:
                role = "user" if msg.sender == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})

            # Inject current sequence into context (if any)
            sequence_steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
            if sequence_steps:
                sequence_text = "\n\n".join(
                    [f"Step {step.step_number}: {step.content}" for step in sequence_steps]
                )
                messages.append({
                    "role": "system",
                    "content": f"Here is the current outreach sequence for context:\n\n{sequence_text}"
                })

            # Send to OpenAI
            ai_result = chat_with_openai(messages, session_id=session_id)

            ai_response_text = ai_result["reply"]
            ai_sequence = ai_result.get("sequence")

            # Store AI message in DB
            ai_msg = Message(session_id=session_id, sender="ai", content=ai_response_text)
            db.session.add(ai_msg)
            db.session.commit()

            # If a sequence was generated, save it
            if ai_sequence:
                print(f"Received sequence from OpenAI for session_id: {session_id}")  # Debug log
                SequenceStep.query.filter_by(session_id=session_id).delete()
                db.session.commit()  # Commit the delete first

                for step in ai_sequence:
                    new_step = SequenceStep(
                        session_id=session_id,
                        step_number=step["step_number"],
                        content=step["content"]
                    )
                    db.session.add(new_step)
                db.session.commit()

                # Fetch the saved sequence to ensure it's properly serialized
                saved_sequence = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
                print(f"Retrieved saved sequence for session_id {session_id}: {len(saved_sequence)} steps")  # Debug log
                
                sequence_data = [
                    {
                        "step_number": step.step_number,
                        "content": step.content
                    }
                    for step in saved_sequence
                ]
                # Emit updated sequence over WebSocket
                socketio.emit("sequence_updated", {
                    "session_id": session_id,
                    "sequence": sequence_data
                })
            else:
                sequence_data = []  # Return empty array instead of None

            # Return structured response
            response_data = {
                "response": ai_response_text,
                "sequence": sequence_data
            }
            print(f"Sending response for session_id {session_id}: {response_data}")  # Debug log
            return jsonify(response_data)

        except Exception as e:
            db.session.rollback()  # Rollback any failed database operations
            import traceback
            traceback.print_exc()  # print full stack trace to console
            return jsonify({"error": str(e)}), 500

    @app.route("/sequence/<int:session_id>", methods=["GET"])
    def get_sequence(session_id):
        steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()

        return jsonify([
            {
                "step_number": step.step_number,
                "content": step.content
            }
            for step in steps
        ])
    
    @app.route("/signup", methods=["POST"])
    def signup():
        data = request.get_json()

        # Optional: check if user already exists
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            return jsonify({"message": "User already exists"}), 409

        user = User(
            name=data["name"],
            email=data["email"],
            company=data["company"],
            title=data["title"],
            industry=data["industry"],
            preferences=data.get("preferences", {})
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created", "user_id": user.id})
    
    @app.route("/sessions", methods=["POST"])
    def create_session():
        data = request.get_json()
        user_id = data.get("user_id")
        session_title = data.get("session_title", "New Chat")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        print(f"Creating new session for user_id: {user_id}")  # Debug log

        new_session = Session(
            user_id=user_id,
            session_title=session_title
        )
        db.session.add(new_session)
        db.session.commit()

        print(f"Created new session with id: {new_session.id}")  # Debug log

        return jsonify({
            "message": "Session created",
            "session_id": new_session.id,
            "session_title": new_session.session_title
        })
    
    @app.route("/sessions", methods=["GET"])
    def get_sessions():
        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()

        return jsonify([
            {
                "session_id": s.id,
                "session_title": s.session_title,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ])

    @app.route("/sessions/<session_id>/messages", methods=["GET"])
    def get_session_messages(session_id):
        messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()

        return jsonify([
            {
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ])

    @app.route("/sessions/<session_id>", methods=["PATCH"])
    def update_session(session_id):
        data = request.get_json()
        session = Session.query.get_or_404(session_id)
        
        if "session_title" in data:
            session.session_title = data["session_title"]
        
        db.session.commit()
        return jsonify({
            "message": "Session updated",
            "session_id": session.id,
            "session_title": session.session_title
        })

    @app.route("/sessions/<session_id>", methods=["DELETE"])
    def delete_session(session_id):
        session = Session.query.get_or_404(session_id)
        
        # Delete all messages and sequence steps associated with this session
        Message.query.filter_by(session_id=session_id).delete()
        SequenceStep.query.filter_by(session_id=session_id).delete()
        
        # Delete the session itself
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({"message": "Session deleted successfully"})

    @app.route("/sessions/<session_id>", methods=["GET"])
    def get_session(session_id):
        session = Session.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        return jsonify({
            "session_id": session.id,
            "session_title": session.session_title,
            "created_at": session.created_at.isoformat()
        })

    return app
