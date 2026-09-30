import json

import pytest
from common_utils.common_enums import Actions, EnumEncoder, Rotations
from common_utils.grid_utils import (
    find_nearest,
    find_objects,
    find_particles_location,
    find_tiles,
    get_nearest_free_location,
)
from common_utils.think_utils import simple_chase
from common_utils.utils import OBJ_TYPE_LIST, get_types_dict, obj_fut, replace_with_html
from singleton import realm
from type_defs.objects.cow import Cow
from type_defs.objects.fox import Fox
from type_defs.objects.grass import Grass
from type_defs.particles.eating_particle import EatingParticle


class TestCommonEnums:
    def test_rotations_values(self):
        assert Rotations.UP.value == 1
        assert Rotations.RIGHT.value == 2
        assert Rotations.DOWN.value == 3
        assert Rotations.LEFT.value == 4

    def test_actions_values(self):
        assert Actions.ROTATE_UP.value == 1
        assert Actions.ROTATE_RIGHT.value == 2
        assert Actions.ROTATE_DOWN.value == 3
        assert Actions.ROTATE_LEFT.value == 4
        assert Actions.MOVE_FORWARD.value == 6

    def test_enum_encoder(self):
        payload = {"rotation": Rotations.UP, "action": Actions.MOVE_FORWARD, "val": 42}
        serialized = json.dumps(payload, cls=EnumEncoder)
        deserialized = json.loads(serialized)
        assert deserialized["rotation"] == 1
        assert deserialized["action"] == 6
        assert deserialized["val"] == 42


class TestUtils:
    def test_replace_with_html(self):
        result = replace_with_html("Line 1\nLine 2\nLine 3")
        assert result == "Line 1<br>Line 2<br>Line 3"

    def test_obj_fut_string_resolution(self):
        for type_name in OBJ_TYPE_LIST:
            cls = obj_fut(type_name)
            assert cls is not None
            assert hasattr(cls, "type_name")
            assert cls.type_name == type_name

    def test_obj_fut_non_string_pass_through(self):
        assert obj_fut(Cow) is Cow

    def test_obj_fut_unknown_raises(self):
        with pytest.raises(Exception, match="not found"):
            obj_fut("NonExistentObjectType")

    def test_get_types_dict(self):
        types_dict = get_types_dict()
        assert len(types_dict) == len(OBJ_TYPE_LIST)
        for name, cls in types_dict.items():
            assert name in OBJ_TYPE_LIST
            assert cls.type_name == name


class TestGridUtils:
    def test_find_nearest_single_type(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        grass_close = Grass(x_new=2, y_new=4)
        grass_far = Grass(x_new=2, y_new=8)

        nearest = find_nearest(cow, "Grass", rad=5)
        assert nearest is not None
        assert nearest.index == grass_close.index

    def test_find_nearest_list_of_types(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=1, y_new=1)
        fox = Fox(x_new=3, y_new=1)

        nearest = find_nearest(cow, ["Fox", "Grass"], rad=5)
        assert nearest is not None
        assert nearest.index == fox.index

    def test_find_nearest_not_found(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=0, y_new=0)
        Grass(x_new=9, y_new=9)

        nearest = find_nearest(cow, "Grass", rad=3)
        assert nearest is None

    def test_find_objects_and_locations(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=5, y_new=5)
        grass = Grass(x_new=6, y_new=5)
        fox = Fox(x_new=5, y_new=6)

        found = find_objects(cow, rad=2)
        assert cow.index in found
        assert grass.index in found
        assert fox.index in found

    def test_find_tiles_and_locations(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=5, y_new=5)
        tiles = find_tiles(cow, rad=1)
        # rad=1 on (5,5) tests range(4,6)xrange(4,6) = 4 tiles
        assert len(tiles) == 4
        assert (5, 5) in tiles
        assert (4, 4) in tiles

    def test_find_particles_and_locations(self, setup_small_grid):
        setup_small_grid(10, 10)
        particle = EatingParticle(x_new=4, y_new=4)
        found = find_particles_location(4, 4, rad=2)
        assert particle.index in found

    def test_get_nearest_free_location(self, setup_small_grid):
        setup_small_grid(10, 10)
        Cow(x_new=5, y_new=5)
        free_x, free_y = get_nearest_free_location(5, 5)
        assert (free_x, free_y) != (5, 5)
        assert realm.TILES[(free_x, free_y)].occupied_by is None


class TestThinkUtils:
    def test_simple_chase_toward_target(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        cow.rotation = Rotations.UP
        Grass(x_new=4, y_new=2)
        cow.variables["mode"] = "chase"
        cow.variables["chasing_num"] = 1
        cow.variables["chasing_dir"] = True  # horizontal first

        intent = simple_chase(cow, chase_after=["Grass"], chase_from=[])
        # Cow is at x=2, grass at x=4. Rotation should turn right or move forward
        assert intent in [Actions.ROTATE_RIGHT, Actions.MOVE_FORWARD]

    def test_simple_chase_flee_predator(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        Fox(x_new=3, y_new=2)
        cow.variables["chasing_dir"] = True

        intent = simple_chase(cow, chase_after=["Grass"], chase_from=["Fox"])
        assert cow.variables["mode"] == "run_away"
        assert intent is not None
