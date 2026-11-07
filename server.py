from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import chat, chat_stream
from db import init_db, list_favorites, delete_favorite, save_messages, load_messages, list_conversations, delete_conversation
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

init_db()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],      
)

sessions = {}   # session_id -> that conversation's history list
TITLE_LENGTH = 30


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
        saved = load_messages(session_id)
        sessions[session_id] = [types.Content.model_validate_json(s) for s in saved]  

    history = sessions[session_id]
    count_before = len(history)

    reply = chat(history, req.message)

    new_messages = history[count_before:]                                    
    save_messages(session_id, [m.model_dump_json(exclude_none=True) for m in new_messages])  

    return ChatResponse(reply=reply, session_id=session_id)

@app.post("/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid4())

    if session_id not in sessions:
        saved = load_messages(session_id)
        sessions[session_id] = [types.Content.model_validate_json(s) for s in saved]

    history = sessions[session_id]
    count_before = len(history)

    def generate():
        try:
            for piece in chat_stream(history, req.message):
                yield piece
        except Exception:
            del history[count_before:]              
            raise
        new_messages = history[count_before:]
        save_messages(session_id, [m.model_dump_json(exclude_none=True) for m in new_messages])

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Session-Id": session_id},              
    )

@app.get("/favorites")
def favorites_endpoint():
    rows = list_favorites()    
    return [{"id": row_id, "title": title} for row_id, title in rows]

@app.get("/history/{session_id}")
def history_endpoint(session_id: str):
    saved = load_messages(session_id)
    messages = []
    for s in saved:
        content = types.Content.model_validate_json(s)
        text = "".join(p.text for p in (content.parts or []) if p.text)
        if not text:
            continue                                
        role = "assistant" if content.role == "model" else "user"    
        messages.append({"role": role, "content": text})
    return messages

@app.delete("/favorites/{favorite_id}")
def delete_favorite_endpoint(favorite_id: int):
    deleted = delete_favorite(favorite_id)
    if not deleted:                                   
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"deleted": favorite_id}

@app.get("/conversations")
def conversations_endpoint():
    result = []
    for session_id, first_json in list_conversations():
        try:
            content = types.Content.model_validate_json(first_json)
        except Exception:
            continue                      # skip rows that aren't real messages
        text = "".join(p.text for p in (content.parts or []) if p.text)
        title = text[:TITLE_LENGTH] + ("..." if len(text) > TITLE_LENGTH else "")
        result.append({"session_id": session_id, "title": title or "Untitled chat"})
    return result

@app.delete("/conversations/{session_id}")
def delete_conversation_endpoint(session_id: str):
    deleted = delete_conversation(session_id)
    sessions.pop(session_id, None)                    # blank 2
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": session_id}