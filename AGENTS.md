# Pymageddon agent notes

- Game code lives in `app/` (run scripts from `app/`, or rely on pytest's `pythonpath`). Use the local venv: `.venv/bin/python`.
- **Adding or changing objects (animals, plants, inanimate objects), the food web, sprites, or ecosystem balance:** follow the `add-game-objects` skill in `.github/skills/add-game-objects/SKILL.md`. New types are data in `app/type_defs/objects/wildlife_specs.py`; don't hand-write new class files.
- Tests: `.venv/bin/python -m pytest -q` (includes a ~25s ecosystem simulation that must stay stable).
- Lint/format like pre-commit: isort + black (`--config=pyproject.toml`), flake8 (`--config=.flake8`).
- Sprites are generated via ComfyUI at `localhost:8080` (`app/common_utils/run_comfy_graph.py`). Every prompt and seed is recorded in `images/generated_sprites/manifest.json`.
