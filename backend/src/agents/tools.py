from database.models import SequenceStep, db
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_sequence(role: str, location: str, tone: str, session_id: int, step_count: int = None) -> str:
    base_prompt = f"""
Generate an outreach sequence for recruiting a {role} based in {location}.
Use a {tone} tone.
Respond in JSON format as a list like:
[
  {{ "step_number": 1, "content": "..." }},
  ...
]
"""

    if step_count:
        base_prompt = f"Generate a {step_count}-step outreach sequence for a {role} in {location} with a {tone} tone.\n" + base_prompt

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            { "role": "system", "content": "You are a recruiting assistant that creates candidate outreach sequences." },
            { "role": "user", "content": base_prompt }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    try:
        steps_json = json.loads(content)
    except json.JSONDecodeError as e:
        # Try to extract just the JSON part using regex
        try:
            json_str = re.search(r"\[.*\]", content, re.DOTALL).group()
            steps_json = json.loads(json_str)
        except Exception:
            return f"⚠️ Failed to parse sequence steps: {str(e)}\n\nRaw content:\n{content}"

    SequenceStep.query.filter_by(session_id=session_id).delete()

    for step in steps_json:
        sequence_step = SequenceStep(
            session_id=session_id,
            step_number=step["step_number"],
            content=step["content"]
        )
        db.session.add(sequence_step)

    db.session.commit()

    return "Outreach sequence generated and saved."


tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "generate_sequence",
            "description": "Generates a candidate outreach sequence based on role, location, and tone",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role being hired for"},
                    "location": {"type": "string", "description": "Where the job is based"},
                    "tone": {"type": "string", "description": "Tone of the outreach (e.g., casual, professional)"},
                    "step_count": { "type": "integer", "description": "Optional. Number of outreach steps to include",
        }
                },
                "required": ["role", "location", "tone"]
            }
        }
    }
]