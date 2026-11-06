# Decisions

This document records the major choices in the project, why each was made, and what each one costs.

## Hand-written agent loop instead of a framework

The loop is written directly against the model SDK because the goal was to learn how agents work. Seeing the loop, the tool calls, and the history shows what frameworks hide. The alternatives were LangGraph, CrewAI, the OpenAI Agents SDK, Pydantic AI, and an Anthropic agent SDK. The cost is more code to write and debug, and the decision is worth revisiting later, now that it is clear what a framework abstracts.

## Gemini free tier instead of a paid API or a local model

No cost was a hard requirement, and Ollama was ruled out after install trouble on a machine with a GTX 1060. The tradeoffs are that model names get retired, rate limits apply, and Google may use free-tier data to improve its products. The mitigation is that every model call lives in `llm.py`, so switching providers is a one-file change.

## SQLite for storage

SQLite needs no setup, ships with Python, and is enough for a single-user portfolio project. It is not suited to many concurrent users, so a deployed version would move to Postgres or something similar.

## Refactor before adding the web layer

The agent loop was mixed with terminal input and output, so it was extracted into `agent.py` before FastAPI was added. That separation let the terminal, the API, and the interface share one implementation instead of duplicating the loop.

## FastAPI backend with a Streamlit interface first

A real HTTP backend with a quick Python interface gave a working UI without frontend code, and it leaves a backend that any later frontend can reuse. It also keeps the API key on the server, out of the browser. React and Next.js remain the plan for V3.

## Per-session conversation history

Each conversation gets a session id that maps to its own history. A server talks to many conversations at once, so a single global history would have mixed them together.

## Every message stored as JSON, tool calls included

The full message objects are persisted as JSON strings in the `messages` table, because the model needs its tool calls and results to continue a conversation correctly after a restart. The cost is that the history endpoint has to filter out non-text messages before showing them to the user.

## Save only after the stream finishes

A turn is written to the database only after the full reply is complete, because an interrupted reply would otherwise leave a half-saved turn that can break the history.

## Session id in the URL

The interface forgets its state on reload, so the session id is kept as a query parameter and a reload can find the same chat. The tradeoff is that the id works like a bookmark. Anyone who has it can read that chat, so a deployed version needs real accounts.

## Deleting is a button, not a chef tool

The chef cannot delete favorites, and the sidebar has a button for each recipe instead. A model can misread a phrase like "get rid of that" and delete the wrong recipe, and deletes cannot be undone, so a button keeps deleting a deliberate action. The system prompt tells the chef to point users to the button.

## The chef saves only on request

With vague tool wording, the chef saved every recipe automatically. The fix was a rule in the system prompt together with a stricter tool docstring, and both were needed.

## Favorite titles shown without database ids

The ids never renumber, so after deletes a lone "9" appeared at the top of a short list, and the sidebar now shows titles only. That left the chef's tools talking in ids the user could no longer see, which was resolved by moving them to recipe names, described below.

## Confirm before deleting

Clicking the delete button now asks for confirmation before anything is removed. Deletes cannot be undone, and one accidental click used to lose a recipe or a whole conversation. The pending item is kept in `st.session_state` because Streamlit reruns the script on every click. The cost is one extra click on every delete, which seemed a fair price for no accidental losses.

## Favorites tools use recipe names, not numbers

The sidebar shows titles only, but the chef's tools still spoke in database ids, which never renumber and made a lone "9" appear after deletes. Switching to list positions would only have moved the problem, since the sidebar shows no numbers to match them against. The tools now use names: `get_favorite` searches titles for the text the user gave, and if several recipes match it asks which one is meant. The ids stay internal to the delete buttons. The tradeoff is that a vague name can match several recipes, which the tool handles by asking.

## Roll back a turn that fails partway

When a streamed reply fails, the server removes the messages that turn had already added to the in-memory history. Without that, the next message in the same chat would send the model a history with an unanswered message or a tool call that never got its result. The handler catches `BaseException` and not just `Exception`, because a client that disconnects mid-reply closes the generator with `GeneratorExit`, which is not an `Exception`. The error is re-raised so the client still learns the reply was cut off.

## Tests run against a temporary database

The tests cover `db.py` and `tools.py` and nothing that calls the model, so they are fast, free, and need no API key. A fixture swaps the `DB_PATH` constant for a file in a temporary folder, which keeps the real data safe and gives every test an empty database. The model-facing code in `agent.py` is not unit tested, because its behavior depends on the model's replies. That part is still checked by hand.