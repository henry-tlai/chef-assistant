from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel
from agent import chat
from db import init_db

init_db()
app = FastAPI()

sessions = {}   # session_id -> that conversation's history list


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid4())

    if session_id not in sessions:
        sessions[session_id] = []     

    history = sessions[session_id]
    reply = chat(history, req.message)                 

    return ChatResponse(reply=reply, session_id=session_id)  