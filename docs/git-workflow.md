# Git Workflow

## Atomic commits

An atomic commit is one logical change that leaves the app working, with a message that fully describes it. A useful test has three parts. The commit should have one reason to exist, so if the message needs "and" for unrelated things it is really two commits. The app should still run after it, so any commit can be checked out safely. And it should be revertible on its own, without breaking unrelated work.

A feature that spans layers can be split by layer as long as each step is safe alone: first a new function that nothing calls yet, then an endpoint that uses it, then a button that calls the endpoint.

## Daily workflow

The routine is to run `git status` to see what changed and `git diff` to see exactly how, then stage specific files and review them before committing.

```
git status
git diff
git add <specific files>
git diff --staged
git commit -m "..."
```

When one file holds two unrelated changes, `git add -p <file>` walks through each chunk, where `y` stages it, `n` skips it, `s` splits it, and `q` quits. To undo staging without losing work, use `git restore --staged <file>`, or `git restore --staged .` for everything.

## Commit message style

Each message starts with a verb, says what the change does for the app, and ends with the file it touched. The verbs used are Added, Changed, Fixed, and Removed, and extra `-m` flags can carry details worth knowing later.

```
Added a new function that lets the chef's reply come back in pieces in llm.py
Added a streaming version of the chef's response loop that still runs tools in agent.py
Added a new endpoint that sends the chef's reply as it is written and saves the chat when it finishes in server.py
Added live display of the chef's reply as it streams in ui.py
Changed the chef's rules so it only saves a favorite when the user asks in prompts.py
```

Commits happen after each tested piece instead of at the end of a session, and debugging leftovers such as test lines under `if __name__ == "__main__":` never get committed.

## Commit order for a layered feature

Layered features are committed in dependency order so that every commit leaves the app working: the data function in `db.py` first, then the endpoint in `server.py`, then the control in `ui.py`, then any behavior changes in `prompts.py` or `tools.py`, and finally the README and docs.

## What never gets committed

The `.env` file, `chef.db`, `venv/`, `__pycache__/`, `.vscode/`, and throwaway scripts in `scratch/` stay out of the repository. The `.gitignore` should list its patterns at the left edge of each line, because leading spaces become part of the pattern and break it.

```
.env
venv/
__pycache__/
*.db
.vscode/
```

## Lessons learned

A broken `.gitignore` fails silently. Indented patterns ignored nothing, which is how `.env` got committed, so it is worth verifying with `git ls-files` and `git check-ignore -v .env` before the first push. A `.gitignore` also only affects untracked files, so anything already tracked needs `git rm --cached <file>`.

GitHub's push protection worked as intended and blocked a push that contained an API key. The "allow the secret" link should not be used. The right response is to remove the secret from the commit and replace the key, and a key that ever sat in a commit should be replaced even if the push was blocked.

PowerShell can save redirected output as UTF-16, so `pip freeze > requirements.txt` produced a file that Git treats as binary. Writing it with `pip freeze | Out-File requirements.txt -Encoding ascii` avoids that. Rewriting unpushed history is safe, with `git commit --amend -m "..."` for the latest commit and `git rebase -i HEAD~N` for several. After rewriting commits that were already pushed, `git push --force-with-lease` is acceptable on a solo repository, but it should never be used on a shared one.

## Before every push

Run `git status`, then `git ls-files` to confirm that `.env`, `chef.db`, `venv/`, and `__pycache__/` do not appear, then `git log --oneline -8` to check that the messages read well, and then `git push`.