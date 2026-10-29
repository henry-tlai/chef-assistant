from google.genai import types
from llm import ask_model
from prompts import SYSTEM_PROMPT
from tools import TOOLS
from db import init_db

init_db()
history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break

    history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

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

    print("Chef:", "".join(p.text for p in reply.parts if p.text))