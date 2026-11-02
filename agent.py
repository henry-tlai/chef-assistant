from google.genai import types
from llm import ask_model, ask_model_stream
from prompts import SYSTEM_PROMPT
from tools import TOOLS

def chat_stream(history, user_message):
    """Yield the chef's reply text in pieces as it's generated."""
    history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    while True:
        parts = []
        for chunk in ask_model_stream(history, SYSTEM_PROMPT, list(TOOLS.values())):
            if not chunk.candidates or not chunk.candidates[0].content:
                continue
            for p in chunk.candidates[0].content.parts or []:
                parts.append(p)
                if p.text and not p.thought:
                    yield p.text                       
                    
        reply = types.Content(role="model", parts=parts)
        history.append(reply)

        calls = [p.function_call for p in parts if p.function_call]
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

def chat(history, user_message):
    return "".join(chat_stream(history, user_message))