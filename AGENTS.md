# Pymageddon agent notes

Pymageddon is a browser MMO survival game built on an ecosystem simulation. It has three processes: a FastAPI server (`app/server.py`), a game node (`app/main.py`, started by `app/run.py`), and Redis between them. For the architecture, API and bot language, see [README.md](README.md).

## Environment
- Game code lives in `app/` (run scripts from `app/`, or rely on pytest's `pythonpath`). Use the local venv: `.venv/bin/python`.
- Redis host is hard-coded as `pymageddon-redis-server`. Tests use `fakeredis` by monkeypatching `server.r`.
- Don't run `app/setup.py build_ext` locally. The Cython `.so` files it produces would shadow `.py` edits.

## Tasks
- **Adding or changing objects (animals, plants, inanimate objects), the food web, sprites, or ecosystem balance:** follow the `add-game-objects` skill in `.github/skills/add-game-objects/SKILL.md`. New types are data in `app/type_defs/objects/wildlife_specs.py`; don't hand-write new class files.
- **Bot language** (`app/sandboxed_language/evaluator.py`): this is a whitelist AST interpreter, not `exec`. Keep it that way. Never add attribute access, imports, loops or arbitrary calls. Expose new helpers only through `function_operators`. Then update the bot reference in `README.md` and `app/templates/llms.txt`.
- **New public page or endpoint:** add the page to `app/templates/sitemap.xml`, and add both pages and endpoints to `app/templates/llms.txt`. If the route is private or authenticated, disallow it in `app/templates/robots.txt`. Give HTML pages `title` and `description` blocks (base template: `_menu_bar.html`). Use the `site_url` Jinja global for absolute URLs.
- **Server secrets:** `SECRET_KEY` in `server.py` is a known placeholder. Don't copy it elsewhere.

## Checks
- Tests: `.venv/bin/python -m pytest -q` (includes a ~25s ecosystem simulation that must stay stable, plus Node frontend tests in `tests/frontend/`). Long equilibrium runs: `pytest -q simulation_tests/`.
- Lint/format like pre-commit: isort + black (`--config=pyproject.toml`), flake8 (`--config=.flake8`).
- Sprites are generated via ComfyUI at `localhost:8080` (`app/common_utils/run_comfy_graph.py`). Every prompt and seed is recorded in `images/generated_sprites/manifest.json`.
