# Chef Assistant

A conversational AI chef that runs in your terminal. Chat about what you feel like eating, get recipe ideas, cook along step by step, and save your favorite recipes for later.

Built in Python with a hand-written agent loop (no framework) so every part of how the agent works is visible in the code.

<!-- Add a screenshot here -->

---

## Features

- **Casual conversation.** The chef chats like a friend and suggests a dish when the moment is right.
- **Consistent recipes.** Title, time and servings, ingredients, and numbered steps with short explanations of why.
- **Cooking mode.** Walks you through a recipe one step at a time.
- **Favorites.** Save a recipe, list your saved recipes, and reopen one by its number. Stored in SQLite, so it persists between sessions.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3 |
| Model | Google Gemini API (free tier) via `google-genai` |
| Agent loop | Hand-written, no framework |
| Storage | SQLite |
| Config | `python-dotenv` |
| Interface | Terminal |

---

## Project Structure

```
chef-assistant/
├── main.py            # chat loop and agent loop (run this)
├── llm.py             # the only file that talks to the model
├── prompts.py         # the chef's system prompt
├── tools.py           # tools the model can call
├── db.py              # SQLite helpers for favorites
├── requirements.txt
└── .env               # your API key (not committed)
```

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

You: what are my favorites?
Chef: You've got 1 saved: 1. One-Pan Garlic Butter Chicken & Rice

You: let's cook number 1
Chef: Step 1: Season the chicken with salt, pepper, and Italian seasoning...
      Tell me when you're ready for the next step.
```

---

## Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com).

2. Clone the repo and create a virtual environment:

   ```bash
   git clone <your-repo-url>
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

5. Run it:

   ```bash
   python main.py
   ```

Type `quit` or `exit` to leave.

---

## How It Works

An agent is a loop: the model decides whether to answer or call a tool, sees the result, and repeats until it has a final answer.

```
User message
     │
     ▼
Add to history ──► Send history + system prompt + tools to the model
                              │
                              ▼
                  Did the model ask to call a tool?
                     │                    │
                    yes                   no
                     │                    │
          Run the tool in Python     Print the reply
          Add the result to history   and wait for the
          and ask the model again     next user message
```

The model never runs code itself. It asks for a tool by name, `main.py` looks it up in the `TOOLS` registry, runs it, and sends the result back.

### Tools

| Tool | What it does |
|---|---|
| `save_favorite` | Saves a recipe to the favorites database |
| `list_favorites` | Lists saved recipes with their numbers |
| `get_favorite` | Loads one saved recipe by number so you can cook it |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `404 NOT_FOUND ... model` | Gemini model names get retired. Change `MODEL` in `llm.py` to a current text model. |
| Empty reply or `NON-TEXT: audio/...` | The model is an audio or image model. Pick a text model. |
| `504 deadline exceeded` | Retry, or try a lighter "flash-lite" model. |
| `ImportError: cannot import name ...` | Save all files and check the names match exactly. |
| `KeyError` when a tool is called | The tool isn't listed in the `TOOLS` dictionary in `tools.py`. |

---

## Roadmap

- [x] **V1:** Terminal chef with conversation, cooking mode, and favorites
- [ ] **V2:** FastAPI backend and a chat UI (Streamlit or Chainlit)
- [ ] **V3:** Full-stack web app with React/Next.js