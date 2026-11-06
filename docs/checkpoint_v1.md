# Chef Assistant V1: Checkpoint Summary

# What we built
A terminal chef agent that chats casually, suggests recipes in a consistent format, walks you through cooking one step at a time, and saves, lists, and reopens favorite recipes from a database. It’s on GitHub with a README.

# Stack we used

**Layer**	**Choice**	**Why**
Language	Python 3	Standard for AI work
Model	Gemini API, free tier (google-genai)	No cost; Ollama and the paid Anthropic API were ruled out
Agent loop	Hand-written, no framework	See exactly how agents work
Storage	SQLite	Zero setup, persists between sessions
Config	python-dotenv and .env	Keeps the API key out of code
Interface	Terminal	Fastest way to get the core working
Tools	Git, GitHub, VS Code, venv	Version control and isolated dependencies
What we learned

# How agents work

An agent is a loop: the model decides whether to answer or call a tool, your code runs the tool, the result goes back, and it repeats.
The model never runs code. It asks for a tool by name, and your code does the work.
The API has no memory, so the full history is sent with every request.
A system prompt defines personality, behavior, and format.
Tool docstrings act as instructions. The model decides when to call a tool based on its name, type hints, and docstring.

# Prompting

Telling the model what to do beats describing how it should sound.
“Ask questions first” produced an interrogation; “chat first, at most one question, suggest when it fits” fixed it. Behavior problems are usually fixed by editing one specific section.
Change one thing at a time and test.

# Engineering

Splitting the code so each file has one job (llm.py, prompts.py, tools.py, db.py, main.py) makes it easy to extend. Swapping model providers touches only llm.py.
Parameterized SQL (? placeholders) handles apostrophes in recipes and avoids injection.
Testing a piece alone (like db.py) before connecting it to the model makes bugs easier to find.

# Debugging lessons

Model names get retired, so a 404 can be a naming problem and not a code problem.
Different model types exist: a model that returned audio/wav wasn’t a text model.
A 504 means your request reached the server and the server timed out, which rules out your network and code.
A Pydantic error showing input_type=function means you passed a function instead of its result.
An ImportError: cannot import name usually means an unsaved file or a misnamed variable.

# Security and Git

A .gitignore with indented lines ignores nothing, since leading spaces become part of the pattern. That’s how .env got committed.
GitHub’s push protection caught the key before it went public.
Verify with git ls-files before every first push, and replace any key that touched a commit.
What this taught us about the project itself
Building the loop by hand made the framework question easier to answer. You now know what a framework would be doing for you.
The free tier works for learning, but it brings model churn, rate limits, and a data-use caveat.
Most of V1’s difficulty was environment and tooling, not AI. That’s normal for a first agent project.

# Where it goes next
**V2:** Refactor the loop into a reusable chat() function, add a FastAPI backend, and build a chat UI with Streamlit or Chainlit.
**V3:** Full-stack web app with React/Next.js and Tailwind.
Later ideas: Pantry tracking, dietary preferences, timers, voice, and trying an agent SDK now that you know what it abstracts.