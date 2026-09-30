import random

import main  # noqa: F401  (registers every object type)
import pytest
from singleton import realm
from type_defs.tiles.tile1 import Tile1
from type_defs.utils.utils import Map


def _reset_world(size):
    realm.__init__()
    realm.MAP = Map(size_x=size, size_y=size)
    realm.SCORE_LIST = {"players": {}, "ranking": {}}
    for i in range(size):
        for j in range(size):
            realm.TILES[(i, j)] = Tile1(x=i, y=j)
    return realm


@pytest.fixture
def empty_world():
    """Returns a factory creating an empty square map of the given size."""
    random.seed(1234)
    yield _reset_world
    realm.__init__()


@pytest.fixture
def run_epochs():
    def _run(count):
        for _ in range(count):
            main.simulate_epoch()
            realm.EPOCH_COUNTER += 1

    return _run
