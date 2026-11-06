# Debugging Log

These are the real problems hit during the build, with their causes and fixes, grouped by the area they came from.

## Setup and model access

The first model error was a `404 NOT_FOUND` for `models/____`, which happened because placeholder blanks were left in the model line. Later a `404` said the model was no longer available to new users, since Gemini model names get retired, and the fix was to use the model the error recommended. One run returned `NON-TEXT: audio/wav` with empty text because an audio model had been selected, and filtering the model list to exclude names containing `audio`, `tts`, `live`, and `image` solved it. A `504 deadline exceeded` meant the model was slow or overloaded, so retrying, raising the timeout, or using a lighter flash-lite model helped. A guessed model name also produced a 404, and the lesson was to list the models for the key and copy a real name.

## Python and imports

An `ImportError: cannot import name 'SYSTEM_PROMPT'`, and later the same for `TOOLS`, came from an unsaved file, a typo, or indentation, and the fix was to save all files and keep the variable at the left margin. A Pydantic error showing `input_type=function` meant the function itself had been appended to the history instead of its result. Swapping the arguments of `chat` produced an `AttributeError` on a string, and using a variable from another file produced a `NameError`. A capitalization typo, `DB_Path` for `DB_PATH`, crashed a delete because Python is case-sensitive. Deleting a conversation failed with `no such table: conversations` because conversations are rows in the `messages` table, and `sessions.content` raised an error because the right dictionary method is `pop`.

## Git and files

GitHub's push protection blocked a push because `.env` had been committed, and the fix was to remove it from the commit before pushing and then replace the API key. The cause was a `.gitignore` whose lines were indented, since leading spaces become part of the pattern and nothing was ignored. `requirements.txt` showed as a binary file because PowerShell's redirect saved it as UTF-16, and writing it with `Out-File -Encoding ascii` fixed it. Staging everything together with `git add .` would have mixed four unrelated changes into one commit, so the staging was undone with `git restore --staged .` and the files were committed one change at a time.

## Web and interface

Visiting the server root returned `{"detail":"Not Found"}` simply because no route exists at `/`, and the `/docs` page was the right place to test. The `/docs` page pre-fills `"session_id": "string"`, so deleting that example field starts a fresh chat. Several interface bugs came from sending or reading the wrong thing: sending the whole `st.session_state` or the whole response instead of one field, saving the reply text as the session id so the chef forgot every turn, and reading `c["title"]` where the id was needed so chat clicks loaded nothing.

The most instructive bug was indentation. The favorites list and the chat list both disappeared when the server was up, because their code had been indented under the `except` block and only ran when the server was down. A `KeyError: 'x-session-id'` appeared when an error response carried no header, and printing the status and body first revealed the real cause. A `405 Method Not Allowed` came from a URL constant that pointed at the wrong route. Finally, streaming looked instant because short replies arrive in only a few chunks, and asking for a long recipe and timing the chunks showed that it was working.

## Behavior

The chef first asked three questions at once, because the prompt told it to ask when the user was vague, and rewriting the section as "chat first, at most one question, suggest when it fits" fixed it. It offered to "rewrite the list" when asked to delete a favorite, since it has no delete tool by design, and a prompt rule now points users to the delete button. It also saved every full recipe on its own because of vague tool wording, which a stricter docstring plus a system prompt rule corrected.

## Habits that helped

Reading the last line of a traceback first usually names the file, the line, and the problem. Testing each layer on its own before connecting it, from the database function to the endpoint to the interface, made bugs easy to place. Running `git status` and then `git diff --staged` before every commit caught stray changes, and when something worked in one place but not another, printing what was actually arriving beat guessing.

## Hardening and testing

The confirmation step brought back the indentation bug. The new favorites loop was pasted one level too deep, under the `except` block, which made the file fail to run with an `IndentationError`, and the fix was to line the loop up with `try:` and `except`. Two of the blanks also reused the marker variable where the value meant "nothing is pending," which would have made Cancel do nothing, and the fix was to reset the state to `None`.

The first pytest run failed with `No module named 'db'` because the tests folder sits one level below `db.py` and plain `pytest` did not put the project folder on the import path. Running `python -m pytest -v` from the project folder fixed it, and it also showed that `pytest.ini` was not being read. The temporary database fixture first failed because it replaced the function `init_db` instead of the `DB_PATH` constant, so the next line tried to call a string. One test then hit a `RecursionError`, because a blank was filled with the test's own name and the test called itself until Python gave up.

Two failures in `tests/test_tools.py` were different in kind. One was a wording mismatch between the test and the message in the tool, and the pytest output printed both strings side by side, which made it quick to fix. The other was a real bug that the test caught: `get_favorite` treated a single matching recipe as several, because the multiple-match condition was true for any match at all. The chef would have asked "which one do you mean?" about a recipe with only one match, and the model often papered over it, which is why hand testing missed it. The fix was to ask for more than one match.

A test written without saving any data first could not check what it claimed to, because deleting from an empty database proves nothing. The isolation test for deleting a conversation needs two saved conversations and a check that the other one survives, and it was confirmed by temporarily removing the `WHERE` clause and watching the test fail.