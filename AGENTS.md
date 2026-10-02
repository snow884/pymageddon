# Pymageddon agent notes

Pymageddon is a browser MMO survival game built on an ecosystem simulation. It has three processes: a FastAPI server (`app/server.py`), a game node (`app/main.py`, started by `app/run.py`), and Redis between them. For the architecture, API and bot language, see [README.md](README.md).

For a dated summary of recent repository work, validation evidence, and the current follow-up item, see [HANDOFF.md](HANDOFF.md).

## Environment
- Game code lives in `app/` (run scripts from `app/`, or rely on pytest's `pythonpath`). Use the local venv: `.venv/bin/python`.
- Redis host is hard-coded as `pymageddon-redis-server`. Tests use `fakeredis` by monkeypatching `server.r`.
- Don't run `app/setup.py build_ext` locally. The Cython `.so` files it produces would shadow `.py` edits.

## Tasks
- **Adding or changing objects (animals, plants, inanimate objects), the food web, sprites, or ecosystem balance:** follow the `add-game-objects` skill in `.github/skills/add-game-objects/SKILL.md`. New types are data in `app/type_defs/objects/wildlife_specs.py`; don't hand-write new class files.
- **Generating any art, animation, or audio with ComfyUI** (`app/common_utils/run_comfy_graph.py`: T2I, image edit, I2V, TTS): follow the `comfyui-assets` skill in `.github/skills/comfyui-assets/SKILL.md`.
- **Particle effects:** server particles in `app/type_defs/particles/` set `fx` (a preset in `FX_PRESETS` in `app/templates/play.html`), and optionally `fx_sheet`/`fx_frames` (an I2V flipbook from `common_utils.generate_particle_fx`) and `fx_label`. The client plays them as real-time effects. Only `ground_stuck` particles (blood, tracks) still render the server-driven `image`.
- **Bot language** (`app/sandboxed_language/evaluator.py`): this is a whitelist AST interpreter, not `exec`. Keep it that way. Never add attribute access, imports, loops or arbitrary calls. Expose new helpers only through `function_operators`. Then update the bot reference in `README.md` and `app/templates/llms.txt`.
- **New public page or endpoint:** add the page to `app/templates/sitemap.xml`, and add both pages and endpoints to `app/templates/llms.txt`. If the route is private or authenticated, disallow it in `app/templates/robots.txt`. Give HTML pages `title` and `description` blocks (base template: `_menu_bar.html`). Use the `site_url` Jinja global for absolute URLs.
- **Client timing / lag** (`app/templates/play.html`, `/get_map`, `/control`): read "Timing and client sync" in `README.md` first. Keep these invariants:
  - Poll with `since_epoch` and keep a single request in flight. Don't go back to a fixed fast `setInterval` that downloads full maps.
  - `update_data()` must start each new segment from the on-screen position (`last_t`), not from the previous target.
  - Animation duration comes from the arrival-interval EMA, not from a hard-coded 0.33.
  - Don't create a `PIXI.Text` (or other per-object canvas resources) for objects that display nothing; tiles churn every time the player moves.
  - Don't log per request in hot endpoints (`get_user` runs on every authenticated call).
  - If the snapshot format or tick rate changes, update `send_map_data` in `main.py`, `refresh_data()` in `play.html`, and the `/get_map` tests in `tests/test_server.py` together.
- **Server secrets:** `SECRET_KEY` in `server.py` is a known placeholder. Don't copy it elsewhere.

## Checks
- Tests: `.venv/bin/python -m pytest -q` (includes a ~25s ecosystem simulation that must stay stable, plus Node frontend tests in `tests/frontend/`). Long equilibrium runs: `pytest -q simulation_tests/`.
- Lint/format like pre-commit: isort + black (`--config=pyproject.toml`), flake8 (`--config=.flake8`).
- Sprites are generated via ComfyUI at `localhost:8080` (`app/common_utils/run_comfy_graph.py`). Every prompt and seed is recorded in `images/generated_sprites/manifest.json`.
