# Repository Handoff

Updated: 2026-10-01

## Current Baseline

- Checkout: `master` at `80ebece` (`add readme and doc files`), matching `origin/master` when checked.
- Worktree was clean at handoff creation.
- Recent terminal history records `git push` completing with exit code 0.
- `AGENTS.md` is the starting point for repository conventions; the add-game-objects workflow is in `.github/skills/add-game-objects/SKILL.md`.

## Recent Work

- `aa301b4` and `c8c1b5c` adjusted simulation/game tests and runtime setup to get the test suites passing.
- `19bb9d6` updated deployment setup and assets, including Docker Compose, Docker build scripts, a workflow file, and wildlife specifications.
- `330d9fb` refreshed the shared layout and styling plus the home, login/account, bot creation, game start, explorer, player, leaderboard, and world-map pages. It also updated ecosystem object specifications and eating behavior. Player-controlled Cow/Cow juvenile objects may eat objects in their diet without the built-in AI's prey-availability restriction; the AI restriction remains in place. Tests cover the Cow/Cow juvenile strawberry diet and player eating behavior.
- `848733d` added page title/description metadata, updated sitemap and robots entries, expanded `/llms.txt` support, and added server and sandbox tests around the discoverability/API changes.
- `80ebece` added the root README, `app/templates/llms.txt`, and agent-facing documentation files.

The main implementation surfaces from this work are `app/server.py`, `app/templates/`, `app/static/website/assets/dist/css/pymageddon.css`, `app/type_defs/objects/effects/eat_object_in_front.py`, `app/type_defs/objects/wildlife_specs.py`, and the tests under `tests/`.

There is also a separate local/remote branch, `feature/ecosystem-130-objects`, at `f3dfb58` (`Expand ecosystem to 130 object types with life cycles and food web`). It is not the current `master` branch. Inspect its status and intended relationship to `master` before cherry-picking or merging anything from it.

## Validation Recorded

Recent terminal history shows isort, Black, Flake8, the full pytest suite, and `simulation_tests/` were run; the recorded command completed with exit code 0. Output was filtered through `grep`, so the exact test counts and individual summaries are not preserved. A later focused Flake8 run for `app/server.py` and `tests/test_server.py`, followed by pytest, also completed with exit code 0. Rerun the checks below when changing these areas:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m pytest -q -p no:cacheprovider simulation_tests/
.venv/bin/flake8 --config=.flake8 app tests simulation_tests
```

## Follow-Up: Bot Editor Preview

The shared browser tab at `http://127.0.0.1:8765/create_bot_page` rendered the page, but its console showed a `401 Unauthorized` and a `TypeError` involving `user_name` at the rendered page's line 189. The exact request and source of the error were not established. Current `_menu_bar.html` requests `/me` when a token exists and checks that the response data and `user_name` are present before updating the account menu. First inspect the browser Network/console details and the served response to identify which request returned 401; distinguish an expected anonymous/expired-token response from an application bug before changing auth behavior. Then verify both anonymous and authenticated bot-editor flows.

An attempted local preview-server setup also failed with exit code 127 because the command was run with an incorrect relative path to the virtual environment. From the repository root, use `.venv/bin/python`; from `app/`, use `../.venv/bin/python`.

## Working Notes

- Run Python/game commands from the repository's `.venv`; run application modules from `app/` where their imports expect it.
- Tests use `fakeredis` for the server Redis dependency. For the real server/game-node workflow, Redis must be reachable at `pymageddon-redis-server`.
- Do not run `app/setup.py build_ext` locally: generated Cython `.so` files can shadow Python source edits.
- The browser snapshot's `401` is not sufficient evidence that login or bot deployment is broken; reproduce with the intended guest/login flow before making a behavioral change.