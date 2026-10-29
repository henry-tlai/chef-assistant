from agent import chat
from db import init_db

init_db()
history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break

    reply_text = chat(history, user_input)           
    print("Chef:", reply_text)