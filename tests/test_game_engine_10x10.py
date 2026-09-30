import json

import fakeredis
from common_utils.utils import OBJ_TYPE_LIST, obj_fut
from main import (
    evaluate_effects,
    evaluate_moves,
    evaluate_player_control,
    evaluate_thinking,
    generate_summary_yaml,
    handle_players,
    main_loop,
    send_map_data_all,
)
from singleton import realm
from type_defs.objects.cow import Cow
from type_defs.tiles.tile1 import Tile1
from type_defs.utils.utils import Map, Spectator


def verify_grid_invariants(map_size=10):
    """Assert that grid invariants are strictly preserved."""
    assert realm.MAP.size_x == map_size
    assert realm.MAP.size_y == map_size

    # Check tile occupancy matches object list
    for (x, y), tile in realm.TILES.items():
        assert 0 <= x < map_size
        assert 0 <= y < map_size
        if tile.occupied_by is not None:
            obj_idx = tile.occupied_by
            assert (
                obj_idx in realm.OBJECT_LIST
            ), f"Tile ({x}, {y}) points to missing object {obj_idx}"
            obj = realm.OBJECT_LIST[obj_idx]
            assert (
                obj.x == x and obj.y == y
            ), f"Object {obj} at ({obj.x}, {obj.y}) does not match tile ({x}, {y})"

    # Check all objects in OBJECT_LIST have matching tile
    for obj_idx, obj in realm.OBJECT_LIST.items():
        assert 0 <= obj.x < map_size, f"Object {obj} x={obj.x} out of bounds"
        assert 0 <= obj.y < map_size, f"Object {obj} y={obj.y} out of bounds"
        tile = realm.TILES[(obj.x, obj.y)]
        assert (
            tile.occupied_by == obj_idx
        ), f"Tile at ({obj.x}, {obj.y}) occupied_by {tile.occupied_by} != {obj_idx}"


class TestGameEngine10x10:
    def test_full_engine_execution_with_all_objects_10x10(self):
        """
        Execute full game engine ticks on a 10x10 world where EVERY object type
        is present, plus human player and coded bot.
        """
        map_size = 10
        realm.MODE = "test"
        realm.MAP = Map(size_x=map_size, size_y=map_size)
        fake_r = fakeredis.FakeRedis()
        realm.REDIS_CONNECTION = fake_r
        realm.TILES.clear()
        realm.OBJECT_LIST.clear()
        realm.PLAYER_LIST.clear()
        realm.SPECTATOR_LIST.clear()
        realm.PARTICLE_LIST.clear()
        realm.OBJ_COUNTER = 0
        realm.SCORE_LIST = {"players": {}, "ranking": {}}

        # 1. Initialize all 100 tiles (10x10)
        for i in range(map_size):
            for j in range(map_size):
                realm.TILES[(i, j)] = Tile1(x=i, y=j)

        # 2. Spawn EVERY registered object type from OBJ_TYPE_LIST onto the grid
        spawn_coords = []
        for x in range(map_size):
            for y in range(map_size):
                spawn_coords.append((x, y))

        assert len(OBJ_TYPE_LIST) <= len(
            spawn_coords
        ), "More object types than 10x10 grid tiles"

        created_objects = []
        for idx, type_name in enumerate(OBJ_TYPE_LIST):
            x, y = spawn_coords[idx]
            cls = obj_fut(type_name)
            obj = cls(x_new=x, y_new=y)
            created_objects.append(obj)

        current_idx = len(OBJ_TYPE_LIST)

        # 3. Add a human controlled Player Cow
        player_x, player_y = spawn_coords[current_idx]
        player_cow = Cow(
            x_new=player_x,
            y_new=player_y,
            is_player=True,
            player_name="test_hero",
        )
        created_objects.append(player_cow)
        current_idx += 1

        # 4. Add a programmable bot Cow with sandboxed code
        bot_code = """
global move_count
if not move_count:
    move_count = 1
else:
    move_count = move_count + 1

if move_count % 2 == 0:
    intent = 'ROTATE_RIGHT'
else:
    intent = 'MOVE_FORWARD'
"""
        bot_x, bot_y = spawn_coords[current_idx]
        bot_cow = Cow(
            x_new=bot_x,
            y_new=bot_y,
            is_player=False,
            player_name="bot_master",
            family_name="bot_master",
            code=bot_code,
        )
        created_objects.append(bot_cow)
        current_idx += 1

        # 5. Add a spectator following the bot
        Spectator(
            obj=bot_cow,
            player_name="spectator_user",
            object_type="object",
            lifetime=100,
            title_indicative_message="Watching bot",
        )

        # Verify initial state invariants
        verify_grid_invariants(map_size=10)
        assert len(realm.OBJECT_LIST) == len(OBJ_TYPE_LIST) + 2
        assert len(realm.PLAYER_LIST) == 1
        assert len(realm.SPECTATOR_LIST) == 1

        # 6. Execute 15 full game engine simulation ticks
        for epoch in range(1, 16):
            realm.EPOCH_COUNTER = epoch

            # Simulate player input via Redis
            fake_r.set(
                "control_test_hero",
                json.dumps(
                    {
                        "ArrowUp": epoch % 2 == 1,
                        "ArrowDown": False,
                        "ArrowLeft": False,
                        "ArrowRight": epoch % 2 == 0,
                    }
                ),
            )

            # Engine cycle steps:
            handle_players()
            evaluate_thinking()
            evaluate_player_control()
            evaluate_effects()
            evaluate_moves()
            send_map_data_all()
            generate_summary_yaml()

            # Verify grid invariants hold after each engine tick
            verify_grid_invariants(map_size=10)

            # Check that map data was published to Redis for player and spectator
            player_map_raw = fake_r.get("map_test_hero")
            if "test_hero" in realm.PLAYER_LIST:
                assert player_map_raw is not None
                player_map = json.loads(player_map_raw)
                assert player_map["global_params"]["status"] == "running"
                assert player_map["global_params"]["map_size_x"] == 10
                assert player_map["player"]["object_id"] == str(player_cow.index)

            spectator_map_raw = fake_r.get("map_spectator_user")
            assert spectator_map_raw is not None

            # Check all_objects_summary in Redis
            summary_raw = fake_r.get("all_objects_summary")
            assert summary_raw is not None
            summary = json.loads(summary_raw)
            assert isinstance(summary, dict)

    def test_main_loop_steps_termination_10x10(self, monkeypatch):
        """Test that main_loop(steps=N) executes the loop and terminates properly on small grid."""
        fake_r = fakeredis.FakeRedis()
        realm.MODE = "test"
        realm.REDIS_CONNECTION = fake_r
        realm.TIME_INTERVAL = 0.001  # Make ticks fast for test

        # Run main loop for 3 steps
        main_loop(steps=3)

        assert realm.EPOCH_COUNTER >= 3
        verify_grid_invariants(map_size=realm.MAP.size_x)
