import os
from openai import OpenAI
from dotenv import load_dotenv
from agents.tools import tool_definitions, generate_sequence
from database.models import SequenceStep
import json


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_openai(messages: list, session_id: int) -> dict:
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
            if tool_call.function.name == "generate_sequence":
                args = json.loads(tool_call.function.arguments)

                # Run the actual function
                generate_sequence(
                    role=args["role"],
                    location=args["location"],
                    session_id=session_id,
                    step_count=args.get("step_count")  # Optional
                )

                # Get the generated sequence
                steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()

                # Format sequence message
                sequence_msg = f"I've generated a {len(steps)}-step outreach sequence for a {args['role']} in {args['location']}."

                # Optional GPT follow-up message
                follow_up_prompt = f"""
                    You just generated an outreach sequence for a {args['role']} in {args['location']}.
                    Now continue the conversation naturally.

                    - Do not introduce yourself again.
                    - Don’t say “Hi” or “Hello”. 
                    - Start with talking about the sequence.
                    - Assume you're already mid-conversation.
                    - Offer helpful follow-up options like tweaking tone, regenerating a step, or uploading a job description.
                    - Respond in a friendly, conversational tone that flows from the last message.
                    - Keep it short and concise.
                    """

                follow_up_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{ "role": "user", "content": follow_up_prompt }]
                )

                follow_up = follow_up_response.choices[0].message.content

                return {
                "reply": f"{sequence_msg}\n\n{follow_up}",
                "sequence": [
                    {"step_number": step.step_number, "content": step.content}
                    for step in steps
                ]
            }

    # Step 4: Otherwise, return plain text response
    return {
    "reply": reply.content,
    "sequence": None
}