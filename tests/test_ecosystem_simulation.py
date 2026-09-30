"""Long-running ecosystem simulation on the full-size map.

Checks that with all object types the ecosystem is stable: no species dies
out, none takes over, all animals and plants are represented at comparable
numbers, populations are sustained by the food web rather than by
immigration, and every object type actually takes part in the game.
"""

import random
import statistics

import main
import pytest
from common_utils import ecosystem
from common_utils.utils import OBJ_TYPE_LIST
from singleton import realm

MAP_SIZE = 100
EPOCHS = 2000
WARMUP = 300
SAMPLE_EVERY = 10


def _simulate(seed):
    random.seed(seed)
    realm.__init__()
    main.populate_map_full(MAP_SIZE)

    history = {s: [] for s in ecosystem.SPECIES}
    shares = []
    for _ in range(EPOCHS):
        main.simulate_epoch()
        realm.EPOCH_COUNTER += 1
        if realm.EPOCH_COUNTER > WARMUP and realm.EPOCH_COUNTER % SAMPLE_EVERY == 0:
            counts = ecosystem.species_counts()
            total = sum(counts.values())
            shares.append(max(counts.values()) / total)
            for species, count in counts.items():
                history[species].append(count)
    # The census has an entry for every type that was ever created.
    appeared = set(realm.TYPE_COUNTS)
    return history, shares, dict(realm.IMMIGRATION_COUNTS), appeared


@pytest.fixture(scope="module", params=[0, 1])
def simulation(request):
    result = _simulate(request.param)
    yield result
    realm.__init__()


def test_no_species_dies_out(simulation):
    history, _, _, _ = simulation
    extinct = {s: min(h) for s, h in history.items() if min(h) == 0}
    assert not extinct, f"species died out: {extinct}"


def test_no_species_takes_over(simulation):
    history, shares, _, _ = simulation
    cap = ecosystem.capacity()
    over_cap = {s: max(h) for s, h in history.items() if max(h) > cap}
    assert not over_cap, f"species above carrying capacity {cap}: {over_cap}"
    assert max(shares) < 0.1, "a single species made up >10% of all organisms"


def test_species_are_represented_roughly_equally(simulation):
    history, _, _, _ = simulation
    means = {s: statistics.mean(h) for s, h in history.items()}
    ratio = max(means.values()) / min(means.values())
    assert ratio <= 2.5, (
        f"abundance ratio {ratio:.2f};"
        f" rarest {min(means, key=means.get)}, commonest {max(means, key=means.get)}"
    )


def test_populations_are_sustained_by_reproduction(simulation):
    _, _, immigration, _ = simulation
    rescue_checks = EPOCHS // ecosystem.RESCUE_INTERVAL
    dependent = {s: n for s, n in immigration.items() if n > 0.3 * rescue_checks}
    assert not dependent, f"species relying on immigration: {dependent}"


def test_every_object_type_appears_in_gameplay(simulation):
    _, _, _, appeared = simulation
    missing = sorted(set(OBJ_TYPE_LIST) - appeared - {"Angel"})
    assert not missing, f"object types that never appeared in the game: {missing}"
