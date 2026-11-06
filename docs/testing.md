# Testing

## What is tested

The automated tests cover `db.py` and `tools.py`. Neither file calls the model, which makes the tests fast, free, and independent of any API key or network connection. The database tests check that favorites can be saved, listed, found by part of their title regardless of capitalization, and deleted, and that deleting something that no longer exists reports failure. They also check that saved messages come back in the order they were saved, and that deleting one conversation leaves every other conversation untouched. The tool tests check the name-based lookup: no match returns a "not found" message, several matches return a message asking which one is meant, and a single match returns the full recipe.

The code that talks to the model, `agent.py` and `llm.py`, is not unit tested. Its behavior depends on what the model replies, so it is checked by hand, by running the app and trying saving, listing, opening, and cooking through a recipe.

## How it works

Every test that touches the database receives a fixture called `temp_db`, defined in `tests/conftest.py`. The fixture replaces the `DB_PATH` constant in `db.py` with a file inside a temporary folder that pytest creates and deletes, and then creates the tables. Every function in `db.py` reads that constant each time it runs, so all of them end up using the temporary database. The result is that each test starts with an empty database, tests cannot affect each other, and the real `chef.db` is never touched.

## Running the tests

From the project folder, with the virtual environment active:

```
python -m pytest -v
```

Running it through `python -m` puts the project folder on the import path, which is what lets the tests import `db` and `tools`. Pytest itself is listed in `requirements-dev.txt`, so people who only want to run the app do not need to install it.

## Habits that worked

A test that has never failed might not be checking anything, so each important test was broken on purpose at least once: changing `LIKE` to `=` made the case-insensitive search test fail, and removing the `WHERE` clause from the delete made the isolation test fail. Tests should name what they protect, so that a failure is readable from the name alone, and they should check a piece of a message rather than the whole string, so a small wording change does not break them. When an assertion fails, pytest prints both values side by side, and reading that output usually shows whether the test or the code is wrong. In this project it showed both: a wording mismatch in the test, and a real bug in `get_favorite` that hand testing had missed.

## What is not covered yet

The endpoints in `server.py` and the interface in `ui.py` have no automated tests. FastAPI ships a test client that could exercise the endpoints without running a server, which would be a natural next step, particularly for the rollback behavior on failed streams.