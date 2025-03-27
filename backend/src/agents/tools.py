from database.models import SequenceStep, db
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, Any, Optional

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def validate_sequence_params(role: str, location: str) -> Optional[str]:
    """Validates the input parameters for sequence generation."""
    if not role or not location:
        return "Missing required parameters: role and location are required"
    if len(role) > 100 or len(location) > 100:
        return "Role and location exceed maximum length limits"
    return None

def generate_sequence(role: str, location: str, session_id: int, step_count: Optional[int] = None) -> str:
    # Validate inputs first
    validation_error = validate_sequence_params(role, location)
    if validation_error:
        return f"{validation_error}"

    base_prompt = f"""
Generate an outreach sequence for recruiting a {role} based in {location}.
Respond in JSON format as a list like:
[
  {{ "step_number": 1, "content": "..." }},
  ...
]
"""

    if step_count:
        base_prompt = f"Generate a {step_count}-step outreach sequence for a {role} in {location}.\n" + base_prompt

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                { 
                    "role": "system", 
                    "content": "You are a recruiting assistant that creates candidate outreach sequences. Generate professional and engaging outreach messages."
                },
                { "role": "user", "content": base_prompt }
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content

        try:
            steps_json = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract just the JSON part using regex
            try:
                json_str = re.search(r"\[.*\]", content, re.DOTALL).group()
                steps_json = json.loads(json_str)
            except Exception as e:
                return f"Failed to parse sequence steps: {str(e)}\n\nRaw content:\n{content}"

        # Validate the structure of each step
        for step in steps_json:
            if not isinstance(step, dict) or "step_number" not in step or "content" not in step:
                return "Invalid step structure in generated sequence"

        # Clear existing steps and save new ones
        SequenceStep.query.filter_by(session_id=session_id).delete()

        for step in steps_json:
            sequence_step = SequenceStep(
                session_id=session_id,
                step_number=step["step_number"],
                content=step["content"]
            )
            db.session.add(sequence_step)

        db.session.commit()
        return "Outreach sequence generated and saved successfully."

    except Exception as e:
        return f"Error generating sequence: {str(e)}"

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "generate_sequence",
            "description": "Generates a candidate outreach sequence based on role and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role being hired for"},
                    "location": {"type": "string", "description": "Where the job is based"},
                    "step_count": {"type": "integer", "description": "Optional. Number of outreach steps to include"}
                },
                "required": ["role", "location"]
            }
        }
    }
]