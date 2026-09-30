---
name: add-game-objects
description: 'Add new object types (animals with life stages, plants, inanimate objects) to the pymageddon ecosystem. Use when: adding a species/animal/plant/object, extending the food chain/food web, generating object sprites with ComfyUI, rebalancing populations, or when ecosystem simulation tests fail after changing diets or timings.'
---

# Adding Game Objects to Pymageddon

New objects are **data-driven**. You normally edit one spec file, generate sprites, check the balance, and update one test constant. You should not need to write new classes.

## Architecture (read before editing)

| File | Role |
|------|------|
| `app/type_defs/objects/wildlife_specs.py` | **Single source of truth** for new species: stages, diets, timings, sprite prompts. Pure data, with no game imports (avoids circular imports). |
| `app/type_defs/objects/wildlife.py` | Factory that builds one class per stage from the specs (`WILDLIFE_CLASSES`, `POPULATE_TYPES`). Classes are direct `BaseObject` subclasses, so the texture preloader picks them up. |
| `app/common_utils/ecosystem.py` | Food web (`DIETS`, `predators_of`), species grouping (`SPECIES`), census, population regulation, balance constants. |
| `app/common_utils/utils.py` | `OBJ_TYPE_LIST` (includes `new_type_names()` automatically) and `obj_fut()`, which falls back to `WILDLIFE_CLASSES`. |
| `app/main.py` | `populate_map_full` (spawns `POPULATE_TYPES`) and `simulate_epoch()` (think → effects → moves → `ecosystem.rebalance()`). |
| `app/common_utils/generate_object_sprites.py` | Sprite generator (ComfyUI Flux T2I + rembg + post-processing). Records everything in `images/generated_sprites/manifest.json`. |
| Original hand-written types | `cow.py`, `fox.py`, etc. Their diets live in `EXISTING_ANIMAL_DIETS`, and the juveniles added for them in `EXISTING_ANIMAL_JUVENILES`. |

Flee lists are **derived automatically**: an animal flees every type whose diet contains it. Never hard-code `chase_from`.

## Procedure

### 1. Add the spec (`wildlife_specs.py`)

**Animal:** add an entry to `ANIMALS` with at least 3 stages, in life-cycle order:
- The first stage is `kind: "egg"`. It is stationary and hatches after `hatch_time`. Adults lay this stage.
- Then `"juvenile"`. It moves and eats, and grows after `grow_time`. It may override `diet` and `speed`.
- Optionally `"pupa"`. It is stationary and needs `pupa_time`.
- The last stage is `"adult"`. It lays the first stage every `lay_time` when `hp >= breed_hp`.

Required keys: `rgb`, `lay_time`, `hatch_time`, `grow_time`, `hp_skip` (lose 1 hp every N epochs), `speed` (0–1 chance to act per epoch), `stages`, `diet`. Optional keys: `breed_hp` and `breed_cost` (small r-strategists use 45/10; the defaults are `BREED_MIN_HP`/`BREED_HP_COST`), and `pupa_time`.

Each stage needs `name` (CamelCase type name), `kind`, `image` (snake_case file stem), `prompt` (sprite subject) and `desc`.

**Plant (or growing stone/mineral):** add an entry to `PLANTS` with `seed` and `plant` stage dicts, plus `rgb`, `emit_time`, `sprout_time` and `lifespan_skip` (plants die of old age; this keeps seeds flowing). For a 3-stage life cycle (seed/berry/nut → sapling → mature), also add a `sapling` stage dict and `grow_time`. Examples: `AppleTree`, `LivingStones` (lithops) and `SaltDeposit` (a mineral that grows crystals and erodes).

**Inanimate object:** add an entry to `INANIMATE` with `image`, `rgb`, `prompt` and `desc`. These have no effects.

### 2. Wire it into the food web

- Give the new animal a `diet` of existing types, and add the new species' stages to **other** species' diets so it is also prey. Every animal must eat something and be eaten by some other species (tested).
- Every plant must be eaten by someone (tested).
- Diet values are raw hp gains; `FOOD_ENERGY_MULTIPLIER` scales them. Rough guide: seeds 10, plants 15–30, eggs 20–25, juveniles 25–30, adults 40–50.
- To make the carnivorous flower trap the animal, add it to `CARNIVOROUS_FLOWER_PREY`.

### 3. Update the type-count test

`tests/test_object_types.py::test_there_are_130_distinct_object_types` asserts the total. Rename it and update it to the new count.

### 4. Generate sprites (ComfyUI must be running at `localhost:8080`)

```bash
cd app
../.venv/bin/python -m common_utils.generate_object_sprites --only new_image_a,new_image_b
../.venv/bin/python -m common_utils.sprite_contact_sheet /tmp/sheet.png new_image_a,new_image_b
```

- Only write the `prompt` **subject**. The generator wraps it in `CAR_TEMPLATE` (adults and juveniles) or `STATIC_TEMPLATE` (everything else).
- Style to match: top-down orthographic view, transparent background, soft drop shadow to the lower right, 676×676 RGBA. **Animals are cartoon cars dressed as the animal, front facing up.** Juveniles are "small cute" cars; eggs and nests are painterly static objects.
- View the contact sheet. Car sprites are rotated 180° by default because Flux draws them nose-down. If the head is not at the top, add the image to `ROTATION_OVERRIDES` (degrees counter-clockwise from the raw image) and re-run with `--postprocess-only --only <name>` (raw images are in `/tmp/pymageddon_sprites`).
- If a sprite is off-style (e.g. a realistic animal instead of a car), add `SEED_OFFSETS["<name>"] = 1` (increment on each retry) and re-run with `--only <name> --force`. Keep offsets in code so the manifest stays reproducible.
- Commit `images/generated_sprites/manifest.json`. It records the final prompt, seed and parameters for each sprite. Log prompt-template experiments in `images/generated_sprites/prompt_experiments.json`.
- The workflow `i_gen_sprite.json` is reproducible via `--build-workflow`.

### 5. Check balance

```bash
.venv/bin/python tests/sim_report.py 3000 0            # per-species table + SUMMARY
.venv/bin/python tests/sim_report.py 3000 0 Rabbit,Fox # + deaths per stage/cause
```

Targets: the `SUMMARY` abundance ratio should be ≤ 2.5 (it is currently ~1.8), no species should be near zero, and immigration should be a small fraction of deaths (~3%). Interpret the columns:
- **High `starve`:** the species can't find food. Broaden its diet, raise `hp_skip`, lower `breed_hp`, or speed up its food plants' `emit_time`.
- **High `eaten`:** too many predators. Adjust the predators' diets.
- **High `immig`:** the species is surviving on rescue immigration, not reproduction. Fix its vital rates.

### 6. Run tests and lint

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider      # includes 2-seed 2000-epoch simulation (~25s)
.venv/bin/isort --settings-path=pyproject.toml <files> && .venv/bin/black --config=pyproject.toml <files>
.venv/bin/flake8 --config=.flake8 app tests
```

## Population regulation (don't remove; tests depend on it)

`ecosystem.py` keeps the ecosystem stable using these mechanisms:
1. **Carrying capacity:** births are blocked when a species is at its limit.
2. **Dominance limit:** the limit is `DOMINANCE_RATIO × mean` species abundance ("kill the winner").
3. **Immigration:** a species below `FLOOR_FRACTION × capacity` gets one immigrant per `RESCUE_INTERVAL`.
4. **Prey switching:** scarce species are neither chased nor eaten.
5. **Satiation:** animals with `hp >= SATIATED_HP` don't hunt.
6. **Food-dependent breeding:** adults need `breed_hp` to breed, and breeding costs `breed_cost`.

Species counts include **all stages**. `realm.TYPE_COUNTS` is maintained in `BaseObject.__init__`/`die`, so never bypass these when creating or removing objects.

## Pitfalls

- **Adding reproduction sources outside the specs breaks balance.** For example, extending the Angel to lay all new species pushed the abundance ratio to 2.9 and was reverted.
- **Bee is special.** Its egg (a honeycomb) hatches only near other animals, and the bee follows the animal that triggered it (`simple_defend`). It has 2 stages, which is the only exception to the 3-stage rule.
- **Juveniles pass bot code on.** A stage's `code_store` defaults to its `code`, so player-bot code survives egg → juvenile → adult. Keep this when editing `_Wildlife.__init__`.
- **Plants need a lifespan.** Without `HpDepletion`, plants fill their cap, stop emitting seeds, and seed eaters starve.
- **Diagnosis before tuning.** Use the cause-of-death columns in `sim_report.py`; balance problems were caused by mechanics as often as by parameters.
- **zsh loops:** `for a b in 1 2 3 4` iterates pairs, and `$var` is not word-split. Use arrays: `F=(a b); cmd $F`.
- **Run from the right place.** Scripts assume `app/` is on `PYTHONPATH` (pytest configures this via `pyproject.toml`). For ad-hoc runs, `cd app` first.
