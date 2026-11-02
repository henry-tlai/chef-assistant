# Chef Assistant

A conversational AI chef you can chat with in the terminal or in a web app. Talk about what you feel like eating, get recipe ideas, cook along step by step, and keep a list of favorite recipes.

Built in Python with a hand-written agent loop (no agent framework), a FastAPI backend, and a Streamlit chat UI, so every layer of how the app works is visible in the code.

<!-- Add a screenshot of the web app here -->

---

## Features

- **Casual conversation.** The chef chats like a friend and suggests a dish when the moment is right.
- **Consistent recipes.** Title, time and servings, ingredients, and numbered steps with short explanations of why.
- **Cooking mode.** Walks you through a recipe one step at a time.
- **Streaming replies.** The chef's answer appears as it is written instead of after a long pause.
- **Favorites.** Save a recipe on request, list your saved recipes, reopen one, and delete one from the sidebar. Stored in SQLite.
- **Saved conversations.** Chats persist across server restarts and page reloads, with a sidebar list to switch between or delete past chats.
- **REST API.** A FastAPI backend any client can use.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.10+ |
| Model | Google Gemini API (free tier) via `google-genai` |
| Agent loop | Hand-written, no framework |
| Backend | FastAPI + Uvicorn |
| UI | Streamlit |
| Storage | SQLite |
| Config | `python-dotenv` |

---

## Project Structure

```
chef-assistant/
├── agent.py           # chat_stream() and chat(): the agent loop
├── llm.py             # the only file that talks to the model
├── prompts.py         # the chef's system prompt
├── tools.py           # tools the model can call
├── db.py              # SQLite helpers for favorites and messages
├── server.py          # FastAPI backend (HTTP endpoints)
├── ui.py              # Streamlit chat UI (calls the backend)
├── main.py            # terminal version (still works)
├── requirements.txt
├── scratch/           # throwaway test scripts
└── .env               # your API key (not committed)
```

Each file has one job. The agent code (`agent.py`, `llm.py`, `prompts.py`, `tools.py`, `db.py`) knows nothing about how it's being used, so the terminal, the API, and the UI all share it.

---

## Example Session

```
You: I'm hungry
Chef: Ha, same. Anything sounding good, or want me to surprise you?

You: surprise me, I have chicken and rice
Chef: Alright, how about one-pan garlic butter chicken and rice...
      [full recipe in the standard format]

You: save that one
Chef: Done, it's in your favorites.

You: let's cook the garlic butter chicken
Chef: Step 1: Season the chicken with salt, pepper, and Italian seasoning...
      Tell me when you're ready for the next step.
```

---

## Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com).

2. Clone the repo and create a virtual environment:

   ```bash
   git clone https://github.com/henry-tlai/chef-assistant.git
   cd chef-assistant
   python -m venv venv
   venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder with one line:

   ```
   GEMINI_API_KEY=your-key-here
   ```

---

## Running It

### Web app (two terminals, both with the virtual environment active)

**Terminal 1: backend**

```bash
uvicorn server:app --reload
```

**Terminal 2: UI**

```bash
streamlit run ui.py
```

The chat page opens at `http://localhost:8501`. The backend's interactive API docs are at `http://127.0.0.1:8000/docs`. Run both commands from the project folder, since the database path is relative.

### Terminal version

```bash
python main.py
```

Type `quit` or `exit` to leave.

---

## Architecture

```
Streamlit UI (ui.py)
     │  POST /chat/stream  {"message": "...", "session_id": "..."}
     ▼
FastAPI (server.py) ── loads this session's history ──► chat_stream() (agent.py)
     ▲                                                        │
     │  reply text in pieces + X-Session-Id header            ▼
     └───────────────────────────────────────────  agent loop ► Gemini (llm.py)
                                                         │
                                                         ▼
                                                   tools.py ► db.py ► SQLite
```

### The agent loop

An agent is a loop: the model decides whether to answer or call a tool, sees the result, and repeats until it has a final answer.

```
Add user message to history ──► Send history + system prompt + tools to the model
                                          │
                                          ▼
                       Stream the reply, passing text along as it arrives
                                          │
                                          ▼
                              Did the model ask to call a tool?
                                 │                    │
                                yes                   no
                                 │                    │
                      Run the tool in Python     Finish the reply
                      Add the result to history
                      and ask the model again
```

The model never runs code itself. It asks for a tool by name, the code looks it up in the `TOOLS` registry, runs it, and sends the result back. Every part of the model's reply, including tool requests, is kept in the history exactly as it was sent.

### Tools available to the chef

| Tool | What it does |
|---|---|
| `save_favorite` | Saves a recipe to the favorites database, only when the user asks |
| `list_favorites` | Lists saved recipes |
| `get_favorite` | Loads one saved recipe so you can cook it |

Deleting a favorite is intentionally not a chef tool. It's a deliberate action done with the delete button in the UI, because a chat model can misread "get rid of that" and the delete can't be undone.

### API endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/chat/stream` | Streams the reply as text; the session id comes back in the `X-Session-Id` header. Omit `session_id` to start a new conversation |
| POST | `/chat` | Same conversation, but returns the full reply as JSON |
| GET | `/history/{session_id}` | The readable messages of a saved conversation |
| GET | `/conversations` | Saved conversations, newest first, titled by the opening message |
| DELETE | `/conversations/{session_id}` | Deletes a saved conversation |
| GET | `/favorites` | Lists saved recipes |
| DELETE | `/favorites/{id}` | Deletes a saved recipe |

### Persistence

Every message, including tool calls and tool results, is stored in a SQLite `messages` table, one row per message, grouped by session id. The server keeps active conversations in memory and rebuilds a conversation from the database when it sees an id it doesn't have, so chats survive restarts. The UI keeps the session id in the page URL, so a reload returns to the same chat. Favorites live in their own table.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `404 NOT_FOUND ... model` | Gemini model names get retired. Change `MODEL` in `llm.py` to a current text model. |
| Empty reply or `NON-TEXT: audio/...` | The model is an audio or image model. Pick a text model. |
| `504 deadline exceeded` | Retry, or try a lighter "flash-lite" model. |
| UI says the server is having issues | Check that `uvicorn server:app --reload` is running in the other terminal. |
| `405 Method Not Allowed` | The UI is sending a request to a route that doesn't accept it. Check the URL constants at the top of `ui.py`. |
| Chats or favorites missing | Start uvicorn from the project folder; the database file is created relative to where it runs. |
| Reply appears all at once | Short replies arrive in only a few chunks. Ask for a long recipe to see the streaming. |
| `ImportError: cannot import name ...` | Save all files and check the names match exactly. |
| `KeyError` when a tool is called | The tool isn't listed in the `TOOLS` dictionary in `tools.py`. |

---

## Roadmap

- [x] **V1:** Terminal chef with conversation, cooking mode, and favorites
- [x] **V2:** FastAPI backend and Streamlit chat UI with favorites, saved conversations, and streaming replies
- [ ] **V3:** Full-stack web app with React/Next.js and Tailwind on the same backend
- [ ] **Ideas:** pantry tracking, dietary preferences, timers, voice, a confirm step before deletes