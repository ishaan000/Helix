import os
from openai import OpenAI
from dotenv import load_dotenv
from agents.tools import (
    tool_definitions,
    generate_sequence,
    revise_step,
    change_tone,
    add_step
)
from database.models import SequenceStep
import json


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_openai(messages: list, session_id: int) -> dict:
    print(f"\nProcessing chat with session_id: {session_id}")  # Debug log
    
    # Step 1: Send user + history messages and tool defs
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tool_definitions,
        tool_choice="auto"
    )

    reply = response.choices[0].message
    # Step 2: If tool is called, extract name + arguments
    if reply.tool_calls:
        for tool_call in reply.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Ensure session_id is included in the arguments
            if "session_id" not in args:
                args["session_id"] = session_id
            
            print(f"→ Tool called: {name}")
            print(f"→ Arguments: {json.dumps(args, indent=2)}")

            if name == "generate_sequence":
                generate_sequence(**args)
            elif name == "revise_step":
                revise_step(**args)
            elif name == "change_tone":
                change_tone(**args)
            elif name == "add_step":
                add_step(**args)

        # After tool execution, fetch updated sequence
        print(f"Fetching sequence for session_id: {session_id}")  # Debug log
        steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
        print(f"Found {len(steps)} steps for session_id: {session_id}")  # Debug log

        # Build a conversational follow-up
        follow_up_prompt = f"""
You just worked on outreach sequence using the function `{name}`.
Now continue the conversation naturally:

- Don't introduce yourself again.
- Do NOT say "Hi" or "Hello".
- Start by commenting on the sequence.
- Offer to revise another step, tweak the tone, or regenerate something.
- Keep it short, conversational, and useful.
"""

        follow_up_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{ "role": "user", "content": follow_up_prompt }]
        )

        follow_up = follow_up_response.choices[0].message.content

        sequence_data = [
            {"step_number": step.step_number, "content": step.content}
            for step in steps
        ]
        print(f"Returning sequence with {len(sequence_data)} steps")  # Debug log

        return {
            "reply": follow_up,
            "sequence": sequence_data
        }

    # Step 4: Otherwise, return plain text response
    return {
        "reply": reply.content,
        "sequence": []  # Return empty array instead of None
    }