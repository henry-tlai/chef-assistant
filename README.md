# Chef Assistant

A conversational AI chef you can chat with in the terminal or in a web app. Talk about what you feel like eating, get recipe ideas, cook along step by step, and keep a list of favorite recipes.

Built in Python with a hand-written agent loop (no agent framework), a FastAPI backend, and a Streamlit chat UI, so every layer of how the app works is visible in the code.

---

## Features

- **Casual conversation.** The chef chats like a friend and suggests a dish when the moment is right.
- **Consistent recipes.** Title, time and servings, ingredients, and numbered steps with short explanations of why.
- **Cooking mode.** Walks you through a recipe one step at a time.
- **Favorites.** Save a recipe, list your saved recipes, and reopen one by its number. Stored in SQLite, so it persists between sessions.
- **Web UI.** Streamlit chat page with a favorites sidebar that updates after every reply and a delete button for each saved recipe.
- **REST API.** A FastAPI backend any client can use, with separate conversation history per session.

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
├── agent.py           # chat(): runs one user turn through the agent loop
├── llm.py             # the only file that talks to the model
├── prompts.py         # the chef's system prompt
├── tools.py           # tools the model can call
├── db.py              # SQLite helpers for favorites
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

You: let's cook number 1
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

The chat page opens at `http://localhost:8501`. The backend's interactive API docs are at `http://127.0.0.1:8000/docs`.

### Terminal version

```bash
python main.py
```

Type `quit` or `exit` to leave.

---

## Architecture

```
Streamlit UI (ui.py)
     │  POST /chat  {"message": "...", "session_id": "..."}
     ▼
FastAPI (server.py) ── finds this session's history ──► chat() (agent.py)
     ▲                                                       │
     │  {"reply": "...", "session_id": "..."}                ▼
     └──────────────────────────────────────  agent loop ► Gemini (llm.py)
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
                              Did the model ask to call a tool?
                                 │                    │
                                yes                   no
                                 │                    │
                      Run the tool in Python     Return the reply
                      Add the result to history
                      and ask the model again
```

The model never runs code itself. It asks for a tool by name, the code looks it up in the `TOOLS` registry, runs it, and sends the result back.

### Tools available to the chef

| Tool | What it does |
|---|---|
| `save_favorite` | Saves a recipe to the favorites database |
| `list_favorites` | Lists saved recipes with their numbers |
| `get_favorite` | Loads one saved recipe by number so you can cook it |

Deleting a favorite is intentionally not a chef tool. It's a deliberate action done with the delete button in the UI, because a chat model can misread "get rid of that" and the delete can't be undone.

### API endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/chat` | Send a message; returns the reply and a `session_id`. Omit `session_id` to start a new conversation |
| GET | `/favorites` | List saved recipes |
| DELETE | `/favorites/{id}` | Delete a saved recipe (404 if it doesn't exist) |

Conversation history is kept in the server's memory, one list per `session_id`, so it resets when the server restarts. Favorites are stored in SQLite and persist.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `404 NOT_FOUND ... model` | Gemini model names get retired. Change `MODEL` in `llm.py` to a current text model. |
| Empty reply or `NON-TEXT: audio/...` | The model is an audio or image model. Pick a text model. |
| `504 deadline exceeded` | Retry, or try a lighter "flash-lite" model. |
| UI says the server is having issues | Check that `uvicorn server:app --reload` is running in the other terminal. |
| Chef forgets the conversation after a backend restart | Expected: sessions live in memory. Favorites are not affected. |
| `ImportError: cannot import name ...` | Save all files and check the names match exactly. |
| `KeyError` when a tool is called | The tool isn't listed in the `TOOLS` dictionary in `tools.py`. |

---

## Roadmap

- [x] **V1:** Terminal chef with conversation, cooking mode, and favorites
- [x] **V2:** FastAPI backend and Streamlit chat UI with a favorites sidebar and delete
- [ ] **V3:** Full-stack web app with React/Next.js and Tailwind on the same backend
- [ ] **Ideas:** persistent sessions, streaming replies, pantry tracking, dietary preferences, timers, voice
