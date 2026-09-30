import os
import sys

import pytest

# Ensure app directory is on sys.path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import fakeredis
from singleton import realm
from type_defs.tiles.tile1 import Tile1
from type_defs.utils.utils import Map


@pytest.fixture(autouse=True)
def reset_realm():
    """Reset the Realm singleton state before and after every test."""
    fake_r = fakeredis.FakeRedis()
    realm.MODE = "test"
    realm.REDIS_CONNECTION = fake_r
    realm.TILES = {}
    realm.OBJECT_LIST = {}
    realm.SPECTATOR_LIST = {}
    realm.PLAYER_LIST = {}
    realm.PARTICLE_LIST = {}
    realm.OBJ_COUNTER = 0
    realm.MAP_VIEW_SIZE = 11
    realm.TIME_INTERVAL = 0.66
    realm.LAST_REFRESH_TIME = 0.66
    realm.EPOCH_COUNTER = 0
    realm.MAP = Map(size_x=10, size_y=10)
    realm.SCORE_LIST = {"players": {}, "ranking": {}}

    yield realm

    # Cleanup
    realm.TILES.clear()
    realm.OBJECT_LIST.clear()
    realm.SPECTATOR_LIST.clear()
    realm.PLAYER_LIST.clear()
    realm.PARTICLE_LIST.clear()
    realm.OBJ_COUNTER = 0
    realm.EPOCH_COUNTER = 0


@pytest.fixture
def fake_redis():
    """Provides a fresh fake Redis client."""
    return fakeredis.FakeRedis()


@pytest.fixture
def setup_small_grid():
    """Helper to initialize a fully tiled grid of given size."""

    def _create_grid(size_x=10, size_y=10):
        realm.MAP = Map(size_x=size_x, size_y=size_y)
        realm.TILES.clear()
        for i in range(size_x):
            for j in range(size_y):
                realm.TILES[(i, j)] = Tile1(x=i, y=j)
        return realm.MAP

    return _create_grid
