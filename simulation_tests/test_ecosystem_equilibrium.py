"""
Long-running ecosystem stability simulation.

This exercises the *production* world-population code path
(`main.populate_map_full`, the same function `main_loop` uses to seed a fresh
game world) and then runs the production engine tick (`main.simulate_epoch`:
thinking, effects, moves and ecosystem regulation) for a large number of epochs with **no
human players and no bot code** - only the built-in AI (`think()`), hunger/
eating/egg-laying effects, and movement resolution drive the simulation.

The goal is to verify the ecosystem is stable on its own: no animal type (or
the plants/fungi that feed them) permanently dies out, and the total
population settles into an equilibrium instead of collapsing or exploding,
once the simulation has run long enough.

This lives in its own top-level folder (outside `tests/`) on purpose:
`pyproject.toml` sets `testpaths = ["tests"]`, so a plain `pytest` run does
NOT collect this file - it is comparatively slow (tens of thousands of
simulated epochs) and is meant to be run explicitly, e.g.:

    python -m pytest simulation_tests/ -v -s

The number of epochs can be overridden for a quicker smoke run or a longer
soak test:

    ECOSYSTEM_SIM_EPOCHS=1000 python -m pytest simulation_tests/ -v -s
"""

import os
import random
import sys

import pytest

# Ensure app/ is importable regardless of how/where pytest is invoked from.
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import fakeredis  # noqa: E402
from common_utils.ecosystem import SPECIES  # noqa: E402
from main import populate_map_full, simulate_epoch  # noqa: E402
from singleton import realm  # noqa: E402

# Lineages checked for extinction, with every development stage (egg / seed /
# spore, juvenile, adult) - a lineage only dies out when all stages are gone.
LINEAGES = {
    name: tuple(SPECIES[name])
    for name in [
        "Cow",
        "Chicken",
        "Fox",
        "Badger",
        "Bee",
        "Grass",
        "Grass2",
        "Grass3",
        "Mushroom",
        "Mushroom2",
    ]
}

ANIMAL_LINEAGES = ["Cow", "Chicken", "Fox", "Badger", "Bee"]

GRID_SIZE = 50
TOTAL_EPOCHS = int(os.environ.get("ECOSYSTEM_SIM_EPOCHS", 6000))
SAMPLE_EVERY = 50
SEED = 42
# Fraction of the run (counted from the end) considered the "settled"
# window that must show no permanently extinct lineage.
EQUILIBRIUM_WINDOW_FRACTION = 0.2


def _count_by_type():
    counts = {}
    for obj in realm.OBJECT_LIST.values():
        counts[obj.type_name] = counts.get(obj.type_name, 0) + 1
    return counts


def _run_simulation(epochs, sample_every, seed):
    """Seed a fresh world via the real production code path and tick the
    engine forward with no players, recording population snapshots."""
    random.seed(seed)

    realm.MODE = "test"
    realm.REDIS_CONNECTION = fakeredis.FakeRedis()
    realm.TILES = {}
    realm.OBJECT_LIST = {}
    realm.SPECTATOR_LIST = {}
    realm.PLAYER_LIST = {}
    realm.PARTICLE_LIST = {}
    realm.OBJ_COUNTER = 0
    realm.EPOCH_COUNTER = 0
    realm.SCORE_LIST = {"players": {}, "ranking": {}}

    populate_map_full(GRID_SIZE)

    history = [(0, _count_by_type())]
    for epoch in range(1, epochs + 1):
        realm.EPOCH_COUNTER = epoch

        simulate_epoch()

        if epoch % sample_every == 0 or epoch == epochs:
            history.append((epoch, _count_by_type()))

    return history


@pytest.fixture(scope="module")
def ecosystem_history():
    """Run the simulation once and share the population history between
    the assertions below (a full run already takes tens of seconds)."""
    return _run_simulation(TOTAL_EPOCHS, SAMPLE_EVERY, SEED)


class TestEcosystemEquilibrium:
    """
    Verifies that, left to run on its own for a long time, the game
    ecosystem:

    1. Never permanently loses an animal species (or the plants/fungi that
       feed them).
    2. Settles into a stable population equilibrium rather than collapsing
       or exploding.
    """

    def test_no_species_dies_out_over_long_run(self, ecosystem_history):
        equilibrium_window = ecosystem_history[
            -max(1, int(len(ecosystem_history) * EQUILIBRIUM_WINDOW_FRACTION)) :
        ]

        extinct = []
        for name, stages in LINEAGES.items():
            zero_epochs = [
                epoch
                for epoch, cnt in equilibrium_window
                if sum(cnt.get(stage, 0) for stage in stages) == 0
            ]
            if zero_epochs:
                extinct.append((name, zero_epochs))

        assert not extinct, (
            "The following lineages had zero population (no individual in"
            " any development stage) during the equilibrium"
            f" window (last {EQUILIBRIUM_WINDOW_FRACTION:.0%} of a"
            f" {TOTAL_EPOCHS}-epoch run): {extinct}"
        )

        # Sanity check: every animal lineage was actually present at some
        # point during the run, so this test exercises real predator/prey/
        # food dynamics instead of trivially passing on a near-empty map.
        ever_seen = {name: False for name in ANIMAL_LINEAGES}
        for _, cnt in ecosystem_history:
            for name in ANIMAL_LINEAGES:
                if sum(cnt.get(stage, 0) for stage in LINEAGES[name]) > 0:
                    ever_seen[name] = True

        assert all(
            ever_seen.values()
        ), f"Some animal lineages never appeared during the run: {ever_seen}"

    def test_population_reaches_stable_equilibrium(self, ecosystem_history):
        totals = [sum(cnt.values()) for _, cnt in ecosystem_history]
        max_capacity = GRID_SIZE * GRID_SIZE

        # Population must never overflow the grid (one object per tile) and
        # must never collapse to nothing.
        assert all(0 < t <= max_capacity for t in totals), (
            "Total population left the valid [1, grid capacity] range at"
            " some point during the run."
        )

        # Compare the average population of the last quarter of the run to
        # the quarter before it. A genuinely stable equilibrium shouldn't
        # show a runaway trend (crashing towards zero or exploding) between
        # these two late-run windows.
        quarter = max(1, len(totals) // 4)
        settled_avg = sum(totals[-2 * quarter : -quarter]) / quarter
        final_avg = sum(totals[-quarter:]) / quarter

        relative_change = abs(final_avg - settled_avg) / settled_avg
        assert relative_change < 0.5, (
            "Total population changed by more than 50% between the last two"
            f" quarters of the run ({settled_avg:.1f} -> {final_avg:.1f}),"
            " suggesting the ecosystem has not reached equilibrium."
        )
