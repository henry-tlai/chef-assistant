# Checkpoint V2: Backend, Web UI, Saved Chats, Streaming

**Status:** Code complete. The remaining step is pushing the README, docs, and requirements to GitHub.

## Goal

The goal of V2 was to turn the terminal agent into a web app without rewriting the agent, by putting it behind an HTTP API and building a chat interface on top.

## What was built

The work started with a refactor. The agent loop moved out of `main.py` into `agent.py` as `chat(history, user_message)`, so the terminal, the API, and the interface all share one implementation. On top of that sits a FastAPI backend in `server.py` that keeps a separate history for each session id, and a Streamlit chat page in `ui.py` that calls it.

The interface then grew in stages. A favorites sidebar shows saved recipes by title with a delete button for each, and friendly error messages appear when the backend is down. A New chat button resets the conversation and the URL. Conversations became persistent: every message, including tool calls and results, is stored in a SQLite `messages` table, so chats survive server restarts. The session id lives in the page URL, and a history endpoint redraws the chat after a reload. A chat list in the sidebar shows past conversations titled by their opening message, with switching and deleting. Replies now stream, so the chef's answer appears as it is written instead of after a pause.

One behavior bug also got fixed. The chef was saving every full recipe to favorites on its own, and the fix needed both a system prompt rule and a stricter tool docstring so that it saves only when asked.

## Tech stack additions

The backend uses FastAPI with Uvicorn, and the interface uses Streamlit with `requests` to call the backend. Streaming is built from `generate_content_stream` on the model side, `StreamingResponse` on the server side, and `st.write_stream` in the interface. Persistence adds a `messages` table to the existing SQLite database.

## File structure

```
chef-assistant/
├── agent.py           # chat_stream() and chat()
├── llm.py             # ask_model() and ask_model_stream()
├── prompts.py         # system prompt
├── tools.py           # tools and TOOLS registry
├── db.py              # favorites and messages helpers
├── server.py          # FastAPI endpoints
├── ui.py              # Streamlit UI
├── main.py            # terminal version, still works
├── requirements.txt
├── docs/              # these documents
└── scratch/           # throwaway test scripts
```

## Endpoints

`POST /chat/stream` streams the reply and returns the session id in the `X-Session-Id` header, while `POST /chat` returns the full reply as JSON. `GET /history/{session_id}` returns the readable messages of a saved chat, `GET /conversations` lists saved chats newest first, and `DELETE /conversations/{session_id}` removes one. `GET /favorites` lists saved recipes and `DELETE /favorites/{id}` removes one.

## What we learned

On web architecture, the main lesson is that a browser cannot call a Python function. HTTP is the shared language, and FastAPI is the layer that listens for it. The backend acts like a waiter between the interface and the agent, and keeping the agent separate through the refactor is what made adding the web layer easy. A server handles many conversations at once, so state has to be kept per session instead of in one global history, and keeping the API key on the server keeps it out of the browser.

Streamlit taught its own lessons. It reruns the whole script on every interaction, so anything that must survive goes into `st.session_state`. Indentation decides whether code runs at all: two bugs, the missing favorites list and the missing chat list, came from loops accidentally nested under an `except` block. The URL can also hold state through `st.query_params`, which is how the session id survives a reload.

On persistence, the SDK's message objects are Pydantic models, so they convert to and from JSON strings for storage. Tool calls and results have to be stored as well, or the model loses context after a restart, and only the new messages from each turn are saved to avoid duplicates.

On streaming, the benefit is how fast the first words appear, not the total time, so it shows most on long replies. Tool calls arrive inside the stream, so the loop collects every part and rebuilds the full message for the history. The turn is saved only after the stream finishes, which means an interrupted reply leaves no half-saved history.

On agent behavior, the model acts on vague tool descriptions, and a docstring that never said "only when asked" led to automatic saves. Destructive actions such as deleting are also safer as deliberate buttons in the interface than as tools the chat model can call.

## Hardening pass

After the main V2 features were done, a short pass made the app safer without adding features. Deleting a favorite or a chat now asks for confirmation first. The chef's favorites tools were switched from database ids to recipe names, so what the chef says matches what the sidebar shows. A reply that fails or is interrupted partway through is now rolled back on the server and reported clearly in the interface, which keeps the conversation usable afterward. Finally, pytest tests were added for `db.py` and `tools.py`, using a temporary database so real data is never touched. One of those tests caught a real bug in the name lookup before it reached the app.

## Known limitations

Active conversations are held in server memory as well as in the database, which is fine for one user but not for scale. Session ids work like bookmarks, so anyone with an id can read that chat, and a deployed version would need real user accounts. Deletes ask for confirmation but are permanent once confirmed, so there is no undo, and the code that talks to the model in `agent.py` is checked by hand and not by automated tests. Google may use free-tier data to improve its products, so private information should stay out of the chat, and model names get retired over time, so `MODEL` in `llm.py` may need updating.

## How to run

Start the backend with `uvicorn server:app --reload` in one terminal and the interface with `streamlit run ui.py` in another. Both commands run from the project folder, because the database path is relative. The next step is V3, a React and Next.js frontend on the same backend, which already exposes everything a frontend needs.