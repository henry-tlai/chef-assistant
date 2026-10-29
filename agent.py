from google.genai import types
from llm import ask_model
from prompts import SYSTEM_PROMPT
from tools import TOOLS


def chat(history, user_message):
    """Run one user turn through the agent and return the chef's reply as text."""
    history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    while True:
        reply = ask_model(history, SYSTEM_PROMPT, list(TOOLS.values()))
        history.append(reply)

        calls = [p.function_call for p in reply.parts if p.function_call]

        if not calls:
            break

        for call in calls:
            result = TOOLS[call.name](**call.args)
            history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(
                        name=call.name,
                        response={"result": result},
                    )],
                )
            )

    return  "".join(p.text for p in reply.parts if p.text)   # blank: the chef's final text