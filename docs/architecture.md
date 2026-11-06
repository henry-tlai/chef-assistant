# Architecture

## Layers

The interface only talks to the backend, the backend only talks to the agent, and the agent knows nothing about HTTP or Streamlit. That separation is why the terminal version in `main.py` still works unchanged.

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

## Files and their jobs

`main.py` is the terminal interface: it reads input and prints replies. `ui.py` is the Streamlit chat page, with a sidebar for chats and favorites, the chat display, and the calls to the backend. `server.py` holds the HTTP endpoints, keeps the per-session history, and saves and loads conversations. `agent.py` contains the agent loop, where `chat_stream()` yields text and runs tools and `chat()` joins the stream into one string. `llm.py` is the only file that talks to the model, through `ask_model` and `ask_model_stream`. `prompts.py` holds the chef's system prompt, `tools.py` holds the tool functions and the `TOOLS` registry, and `db.py` handles SQLite for both the favorites and messages tables.

## The agent loop

An agent is a loop. The model streams a reply, and text is passed along as it arrives. If the model asked to call a tool, the code runs it, adds the result to the history, and asks the model again. If not, the reply is finished.

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

The model never runs code. It asks for a tool by name, and `TOOLS[name](**args)` runs it. Every part of the model's reply, including tool requests, is kept in the history exactly as it was sent, because the next request fails or loses context otherwise.

## Request flow for one chat turn

The interface posts the message to `/chat/stream`, along with the session id if the chat already exists. The server uses that id or creates a new one, and if the session is not in memory it rebuilds the history from the `messages` table. Then `chat_stream()` runs the loop and yields text pieces, which the server forwards as they arrive, with the session id sent back in the `X-Session-Id` header. When the stream ends, the server saves the new messages from the turn: the user message, any tool calls and results, and the reply. Meanwhile the interface shows the pieces live, stores the finished reply in its state, and reruns so the sidebar refreshes.

If the reply fails or the client disconnects partway through, the server removes everything that turn added to the in-memory history and re-raises the error, so a half-finished turn never lingers. The interface catches the broken stream, shows a short message asking the user to send the message again, and drops the unanswered message from its own list. Because nothing is written to the database until a stream finishes, an interrupted turn is never saved.

## Data model

The database, `chef.db`, has two tables. The `favorites` table has an auto-incrementing `id`, a `title`, and the full `recipe` text. The ids are never reused, which is why gaps appear after deletes. The `messages` table has an auto-incrementing `id` that preserves insert order, a `session_id` that groups messages into a conversation, and a `content` column holding one message as a JSON string, tool calls and results included.

There is no separate conversations table. A conversation is simply the set of rows that share a `session_id`, and its title is taken from its first message.

## Tools and endpoints

The chef has three tools: `save_favorite(title, recipe)`, which saves only when the user explicitly asks; `list_favorites()`, which returns recipe names; and `get_favorite(title)`, which finds a saved recipe by all or part of its name. If more than one recipe matches, the tool tells the chef to ask which one the user means. Database ids stay internal and are used only by the delete buttons. Deleting is deliberately not a tool, and the reasoning is in `decisions.md`.

The backend exposes `POST /chat/stream`, `POST /chat`, `GET /history/{session_id}`, `GET /conversations`, `DELETE /conversations/{session_id}`, `GET /favorites`, and `DELETE /favorites/{id}`. The history endpoint hides tool calls and results, and the delete endpoint for conversations also removes the in-memory copy.

## Where state lives

Favorites and messages live in SQLite and survive restarts. An active conversation's history is held in server memory but can always be rebuilt from the database. The session id lives in the page URL and in `st.session_state`, so a reload finds the same chat through the URL, and the on-screen messages are reloaded from `/history/{id}`.

## Deletion in the interface

Clicking the delete button next to a favorite or a chat does not delete anything. It records which item is waiting for confirmation in `st.session_state.pending_delete`, and that item's row is replaced by a "Delete this?" row with Yes and Cancel buttons. Only Yes sends the delete request, and both buttons clear the pending state afterward. Deleting the chat that is currently open also resets the screen, the session id, and the URL.

## Testing

The tests live in `tests/` and run with `python -m pytest -v`. They cover `db.py` and `tools.py`, which never call the model, so they need no API key and no network. A fixture in `tests/conftest.py` points `db.py` at a temporary database for each test, so the real `chef.db` is never touched. The full description is in `testing.md`.