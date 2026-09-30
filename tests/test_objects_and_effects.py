import pytest
from common_utils import ecosystem
from common_utils.common_enums import Actions, Rotations
from singleton import realm
from type_defs.objects.angel import Angel
from type_defs.objects.badger import Badger
from type_defs.objects.badger_egg import BadgerEgg
from type_defs.objects.bee import Bee
from type_defs.objects.bee_egg import BeeEgg
from type_defs.objects.carnivorous_flower import CarnivorousFlower
from type_defs.objects.carnivorous_flower_seed import CarnivorousFlowerSeed
from type_defs.objects.chicken import Chicken
from type_defs.objects.chicken_egg import ChickenEgg
from type_defs.objects.cow import Cow
from type_defs.objects.cow_egg import CowEgg
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.eat_object_stepping_in import EatObjectSteppingIn
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.objects.effects.turn_into import TurnInto
from type_defs.objects.effects.turn_into_near_object import TurnIntoNearObject
from type_defs.objects.fox import Fox
from type_defs.objects.fox_egg import FoxEgg
from type_defs.objects.grass import Grass
from type_defs.objects.grass2 import Grass2
from type_defs.objects.grass3 import Grass3
from type_defs.objects.mushroom import Mushroom
from type_defs.objects.mushroom2 import Mushroom2
from type_defs.objects.seed import Seed
from type_defs.objects.seed2 import Seed2
from type_defs.objects.seed3 import Seed3
from type_defs.objects.spore import Spore
from type_defs.objects.spore2 import Spore2
from type_defs.objects.stone import Stone
from type_defs.objects.stone2 import Stone2
from type_defs.particles.eating_particle import EatingParticle
from type_defs.tiles.tile1 import Tile1


class TestBaseObjectLifecycle:
    def test_object_creation_and_indexing(self, setup_small_grid):
        setup_small_grid(10, 10)
        obj1 = Cow(x_new=2, y_new=3)
        obj2 = Fox(x_new=4, y_new=5)

        assert obj1.index in realm.OBJECT_LIST
        assert obj2.index in realm.OBJECT_LIST
        assert obj1.index != obj2.index
        assert realm.TILES[(2, 3)].occupied_by == obj1.index
        assert realm.TILES[(4, 5)].occupied_by == obj2.index

    def test_occupied_tile_raises_exception(self, setup_small_grid):
        setup_small_grid(10, 10)
        Cow(x_new=1, y_new=1)
        with pytest.raises(Exception, match="already occupied"):
            Fox(x_new=1, y_new=1)

    def test_movement_within_bounds(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        success = cow.move_to_position(2, 3)

        assert success is True
        assert cow.x == 2
        assert cow.y == 3
        assert realm.TILES[(2, 2)].occupied_by is None
        assert realm.TILES[(2, 3)].occupied_by == cow.index

    def test_movement_out_of_bounds_blocked(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=0, y_new=0)
        assert cow.move_to_position(-1, 0) is False
        assert cow.move_to_position(0, -1) is False
        assert cow.x == 0 and cow.y == 0

        cow_edge = Cow(x_new=9, y_new=9)
        assert cow_edge.move_to_position(10, 9) is False
        assert cow_edge.move_to_position(9, 10) is False

    def test_movement_onto_occupied_blocked(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        Fox(x_new=2, y_new=3)
        success = cow.move_to_position(2, 3)
        assert success is False
        assert cow.x == 2 and cow.y == 2

    def test_get_next_coords(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=5, y_new=5)
        cow.intent = Actions.MOVE_FORWARD

        cow.rotation = Rotations.UP
        assert cow.get_next_coords(1) == (5, 4)
        assert cow.get_next_coords(-1) == (5, 6)

        cow.rotation = Rotations.RIGHT
        assert cow.get_next_coords(1) == (6, 5)

        cow.rotation = Rotations.DOWN
        assert cow.get_next_coords(1) == (5, 6)

        cow.rotation = Rotations.LEFT
        assert cow.get_next_coords(1) == (4, 5)

    def test_score_increment_and_particles(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=3, y_new=3)
        cow.is_alive = True
        cow.score = 19
        cow.run_effects()
        assert cow.score == 20
        # Particle spawned on score 20
        assert len(realm.PARTICLE_LIST) > 0

    def test_die_clears_tile_and_object_list(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=3, y_new=3, is_player=True, player_name="player1")
        cow_idx = cow.index

        cow.die(player_afterlife=False)
        assert realm.TILES[(3, 3)].occupied_by is None
        assert cow_idx not in realm.OBJECT_LIST
        assert "player1" not in realm.PLAYER_LIST


class TestAllObjectTypes:
    def test_all_registered_objects_instantiate(self, setup_small_grid):
        setup_small_grid(10, 10)
        types = [
            Angel,
            Seed,
            Seed2,
            Seed3,
            Grass,
            Grass2,
            Grass3,
            Stone,
            Stone2,
            Chicken,
            Cow,
            Fox,
            ChickenEgg,
            CowEgg,
            FoxEgg,
            CarnivorousFlowerSeed,
            CarnivorousFlower,
            Mushroom,
            Mushroom2,
            Spore,
            Spore2,
            Badger,
            BadgerEgg,
            Bee,
            BeeEgg,
        ]

        idx = 0
        for x in range(5):
            for y in range(5):
                if idx < len(types):
                    cls = types[idx]
                    obj = cls(x_new=x, y_new=y)
                    assert obj.type_name == cls.type_name
                    assert obj.image != ""
                    assert isinstance(obj.get_description_short(), str)
                    assert isinstance(obj.get_description_long(), str)
                    idx += 1


class TestEffects:
    @pytest.fixture(autouse=True)
    def _ignore_prey_scarcity(self, monkeypatch):
        # Lone test animals would otherwise be protected by prey switching.
        monkeypatch.setattr(ecosystem, "hunt_allowed", lambda _type_name: True)

    def test_eat_object_in_front(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=2, y_new=2)
        cow.rotation = Rotations.RIGHT
        cow.intent = Actions.MOVE_FORWARD
        cow.hp = 50

        grass = Grass(x_new=3, y_new=2)
        grass_idx = grass.index

        effect = EatObjectInFront(types_eaten_to_hp_conv={"Grass": 20})
        effect.run_effect(cow)

        assert cow.hp == 70
        assert grass_idx not in realm.OBJECT_LIST

    def test_eat_object_stepping_in(self, setup_small_grid):
        setup_small_grid(10, 10)
        flower = CarnivorousFlower(x_new=5, y_new=5)
        cow = Cow(x_new=5, y_new=4)
        cow.rotation = Rotations.DOWN
        cow.intent = Actions.MOVE_FORWARD

        effect = EatObjectSteppingIn(types_eaten_to_hp_conv={"Cow": 50})
        effect.run_effect(flower)

        assert cow.index not in realm.OBJECT_LIST

    def test_hp_depletion(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=1, y_new=1)
        cow.hp = 10
        effect = HpDepletion(hp_loss_per_cycle=1, skip_cycles=1)
        effect.run_effect(cow)
        assert cow.hp == 9

    def test_turn_into(self, setup_small_grid):
        setup_small_grid(10, 10)
        egg = ChickenEgg(x_new=3, y_new=3)
        egg.variables["turn_into_cycle_counter"] = 10

        effect = TurnInto(future_object_class="Chicken", time_to_turn=5)
        effect.run_effect(egg)

        # Egg died and Chicken spawned at (3, 3)
        assert egg.index not in realm.OBJECT_LIST
        occupied_idx = realm.TILES[(3, 3)].occupied_by
        assert occupied_idx is not None
        assert realm.OBJECT_LIST[occupied_idx].type_name == "Chicken"

    def test_turn_into_near_object(self, setup_small_grid):
        setup_small_grid(10, 10)
        spore = Spore(x_new=4, y_new=4)
        Grass(x_new=4, y_new=5)

        effect = TurnIntoNearObject(
            future_object_class="Mushroom",
            object_class_list_to_turn_when_earby=["Grass"],
        )
        effect.run_effect(spore)

        assert spore.index not in realm.OBJECT_LIST
        occupied_idx = realm.TILES[(4, 4)].occupied_by
        assert realm.OBJECT_LIST[occupied_idx].type_name == "Mushroom"

    def test_lay_object(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=4, y_new=4)
        cow.rotation = Rotations.DOWN
        cow.intent = Actions.MOVE_FORWARD

        effect = LayObject(object_to_lay="CowEgg", time_to_lay=2)
        cow.variables["lay_object_cycle_counter_CowEgg"] = 5
        effect.run_effect(cow)

        # Behind moving down is up (4, 3)
        occupied_idx = realm.TILES[(4, 3)].occupied_by
        assert occupied_idx is not None
        assert realm.OBJECT_LIST[occupied_idx].type_name == "CowEgg"


class TestParticlesAndTiles:
    def test_tile_properties(self):
        tile = Tile1(x=1, y=2)
        assert tile.x == 1
        assert tile.y == 2
        assert tile.occupied_by is None
        d = tile.to_dict()
        assert d["x"] == 1
        assert d["y"] == 2

    def test_particle_lifecycle(self, setup_small_grid):
        setup_small_grid(10, 10)
        particle = EatingParticle(x_new=2, y_new=2)
        p_idx = particle.index
        assert p_idx in realm.PARTICLE_LIST
        assert p_idx in realm.TILES[(2, 2)].occupied_by_particles

        # Run particle cycles until death
        for _ in range(particle.lifetime + 2):
            if p_idx in realm.PARTICLE_LIST:
                particle.effects()

        assert p_idx not in realm.PARTICLE_LIST
