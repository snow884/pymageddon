import importlib
from pathlib import Path

import main
import pytest
from common_utils import ecosystem, image_utils
from common_utils.common_enums import Actions, Rotations
from common_utils.generate_object_sprites import sprite_jobs
from common_utils.grid_utils import find_nearest
from common_utils.utils import OBJ_TYPE_LIST, obj_fut
from PIL import Image
from singleton import realm
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.turn_into import TurnInto
from type_defs.objects.wildlife import WILDLIFE_CLASSES
from type_defs.objects.wildlife_specs import (
    ANIMALS,
    CARNIVOROUS_FLOWER_PREY,
    INANIMATE,
    new_type_names,
)

APP_DIR = Path(__file__).resolve().parent.parent / "app"
ANIMAL_SPECIES = [s for s in ecosystem.SPECIES if s not in ecosystem.PLANT_SPECIES]


@pytest.fixture
def no_immigration(monkeypatch):
    monkeypatch.setattr(ecosystem, "rebalance", lambda: None)


def _image_path(cls):
    return APP_DIR / "static" / "objects" / Path(cls.image).name


# --- Registry -----------------------------------------------------------------


def test_there_are_130_distinct_object_types():
    assert len(OBJ_TYPE_LIST) == 130
    assert len(set(OBJ_TYPE_LIST)) == 130


@pytest.mark.parametrize("type_name", OBJ_TYPE_LIST)
def test_type_resolves_to_class(type_name):
    cls = obj_fut(type_name)
    assert cls.type_name == type_name


@pytest.mark.parametrize(
    ("module_name", "type_name"),
    [
        (f"type_defs.objects.{module}", name)
        for module, names in {
            "cow": ["Cow"],
            "chicken": ["Chicken"],
            "fox": ["Fox"],
            "badger": ["Badger"],
            "cow_egg": ["CowEgg"],
            "chicken_egg": ["ChickenEgg"],
            "fox_egg": ["FoxEgg"],
            "badger_egg": ["BadgerEgg"],
            "grass": ["Grass"],
            "grass2": ["Grass2"],
            "grass3": ["Grass3"],
            "seed": ["Seed"],
            "seed2": ["Seed2"],
            "seed3": ["Seed3"],
            "stone": ["Stone"],
            "stone2": ["Stone2"],
        }.items()
        for name in names
    ],
)
def test_legacy_modules_export_generated_classes(module_name, type_name):
    module = importlib.import_module(module_name)
    assert getattr(module, type_name) is obj_fut(type_name)


@pytest.mark.parametrize("type_name", OBJ_TYPE_LIST)
def test_type_has_sprite(type_name):
    path = _image_path(obj_fut(type_name))
    assert path.exists(), f"missing sprite {path}"


@pytest.mark.parametrize("type_name", new_type_names())
def test_new_sprite_matches_existing_format(type_name):
    with Image.open(_image_path(obj_fut(type_name))) as im:
        assert im.size == (676, 676)
        assert im.mode == "RGBA"
        # Transparent background like the hand-made sprites.
        assert im.getpixel((0, 0))[3] == 0
        assert im.getpixel((675, 675))[3] == 0


def test_sprite_jobs_have_unique_output_images():
    jobs = sprite_jobs()
    output_images = [image for image, _, _ in jobs]
    assert len(output_images) == len(set(output_images))


# --- Life cycles and food web ---------------------------------------------------


@pytest.mark.parametrize("species", ANIMAL_SPECIES)
def test_animals_have_multiple_development_stages(species):
    min_stages = 2 if species == "Bee" else 3
    assert len(ecosystem.SPECIES[species]) >= min_stages


@pytest.mark.parametrize("species", ANIMAL_SPECIES)
def test_every_animal_is_part_of_the_food_chain(species):
    stages = ecosystem.SPECIES[species]
    if species == "CarnivorousFlower":
        return
    eats = [t for t in stages if ecosystem.DIETS.get(t)]
    assert eats, f"{species} eats nothing"

    hunters = {
        ecosystem.SPECIES_OF_TYPE.get(h, h)
        for t in stages
        for h in ecosystem.predators_of(t)
    } - {species}
    assert hunters, f"{species} is eaten by nobody"


@pytest.mark.parametrize(
    "species", sorted(ecosystem.PLANT_SPECIES - {"CarnivorousFlower"})
)
def test_every_plant_is_eaten_by_someone(species):
    eaten = {food for diet in ecosystem.DIETS.values() for food in diet}
    assert eaten & set(ecosystem.SPECIES[species])


def test_food_web_only_references_known_types():
    for eater, diet in ecosystem.DIETS.items():
        assert eater in OBJ_TYPE_LIST
        for food in diet:
            assert food in OBJ_TYPE_LIST, f"{eater} eats unknown {food}"
    for prey in CARNIVOROUS_FLOWER_PREY:
        assert prey in OBJ_TYPE_LIST


def test_food_chain_has_multiple_trophic_levels():
    # plant -> herbivore -> carnivore -> apex predator
    assert "Clover" in ecosystem.DIETS["Rabbit"]
    assert "Rabbit" in ecosystem.DIETS["Fox"]
    assert "Fox" in ecosystem.DIETS["Wolf"]
    assert "Wolf" in ecosystem.DIETS["Bear"]


def test_inanimate_objects_are_passive(empty_world):
    empty_world(10)
    for i, name in enumerate(INANIMATE):
        obj = WILDLIFE_CLASSES[name](x_new=i % 10, y_new=i // 10)
        assert obj.effects is None
        assert obj.think() is None


def test_egg_hatches_into_juvenile_that_grows_into_adult(
    empty_world, run_epochs, no_immigration
):
    empty_world(20)
    spec = ANIMALS["Rabbit"]
    WILDLIFE_CLASSES["RabbitNest"](x_new=10, y_new=10)

    run_epochs(spec["hatch_time"] + 1)
    assert realm.TYPE_COUNTS.get("RabbitNest", 0) == 0
    assert realm.TYPE_COUNTS["Bunny"] == 1

    bunny = next(o for o in realm.OBJECT_LIST.values() if o.type_name == "Bunny")
    bunny.hp = 100
    run_epochs(spec["grow_time"] + 1)
    assert realm.TYPE_COUNTS.get("Bunny", 0) == 0
    assert realm.TYPE_COUNTS["Rabbit"] == 1


def test_butterfly_goes_through_four_stages(empty_world, run_epochs, no_immigration):
    empty_world(20)
    WILDLIFE_CLASSES["ButterflyEgg"](x_new=10, y_new=10)
    seen = set()
    for _ in range(400):
        run_epochs(1)
        for obj in realm.OBJECT_LIST.values():
            obj.hp = 100
            seen.add(obj.type_name)
    assert {"Caterpillar", "Chrysalis", "Butterfly"} <= seen


def test_original_eggs_hatch_into_new_juveniles(
    empty_world, run_epochs, no_immigration
):
    empty_world(20)
    for i, egg in enumerate(["CowEgg", "ChickenEgg", "FoxEgg", "BadgerEgg"]):
        obj_fut(egg)(x_new=2 + 4 * i, y_new=10)
    run_epochs(101)
    for juvenile in ["Calf", "Chick", "FoxKit", "BadgerCub"]:
        assert realm.TYPE_COUNTS.get(juvenile) == 1


def test_bot_code_survives_growing_up(empty_world):
    empty_world(10)
    calf = WILDLIFE_CLASSES["Calf"](x_new=5, y_new=5, code="intent = None")
    grow = next(e for e in calf.effects if isinstance(e, TurnInto))
    calf.variables["turn_into_cycle_counter"] = grow.time_to_turn
    grow.run_effect(calf)

    cow = realm.OBJECT_LIST[realm.TILES[(5, 5)].occupied_by]
    assert cow.type_name == "Cow"
    assert cow.code == "intent = None"


def test_well_fed_adult_lays_eggs(empty_world, run_epochs, no_immigration):
    empty_world(30)
    rabbit = WILDLIFE_CLASSES["Rabbit"](x_new=15, y_new=15)
    for _ in range(300):
        rabbit.hp = 100
        run_epochs(1)
        if realm.TYPE_COUNTS.get("RabbitNest"):
            break
    assert realm.TYPE_COUNTS.get("RabbitNest", 0) >= 1


def test_starving_adult_does_not_breed(empty_world, run_epochs, no_immigration):
    empty_world(30)
    wolf = WILDLIFE_CLASSES["Wolf"](x_new=15, y_new=15)
    wolf.hp = ecosystem.BREED_MIN_HP - 1
    wolf.variables["hp_depletion_cycle_counter"] = -(10**6)
    run_epochs(ANIMALS["Wolf"]["lay_time"] * 2)
    assert realm.TYPE_COUNTS.get("WolfDen", 0) == 0


# --- Population regulation ------------------------------------------------------


def test_census_tracks_births_and_deaths(empty_world, run_epochs):
    empty_world(40)
    main.populate_map_full(40)
    run_epochs(50)
    actual = {}
    for obj in realm.OBJECT_LIST.values():
        actual[obj.type_name] = actual.get(obj.type_name, 0) + 1
    assert {t: c for t, c in realm.TYPE_COUNTS.items() if c} == actual


def test_births_are_blocked_at_carrying_capacity(
    empty_world, run_epochs, no_immigration
):
    empty_world(40)
    limit = ecosystem.capacity()
    for i in range(limit):
        WILDLIFE_CLASSES["Clover"](x_new=(i * 3) % 40, y_new=(i * 3) // 40 * 3)
    assert not ecosystem.birth_allowed("CloverSeed")
    run_epochs(60)
    assert ecosystem.species_count("Clover") <= limit


def test_rare_species_immigrate(empty_world):
    empty_world(40)
    realm.EPOCH_COUNTER = 0
    ecosystem.rebalance()
    for species in ecosystem.SPECIES:
        assert ecosystem.species_count(species) >= 1, species


def _face(obj, rotation):
    obj.rotation = rotation
    obj.intent = Actions.MOVE_FORWARD


def test_scarce_prey_is_spared(empty_world):
    empty_world(40)
    fox = obj_fut("Fox")(x_new=10, y_new=10)
    rabbit = WILDLIFE_CLASSES["Rabbit"](x_new=10, y_new=9)
    fox.hp = 30
    _face(fox, Rotations.UP)
    eat = next(e for e in fox.effects if isinstance(e, EatObjectInFront))

    assert not ecosystem.hunt_allowed("Rabbit")
    eat.run_effect(fox)
    assert rabbit.index in realm.OBJECT_LIST


def test_abundant_prey_is_eaten_by_hungry_predator(empty_world):
    empty_world(40)
    fox = obj_fut("Fox")(x_new=10, y_new=10)
    rabbit = WILDLIFE_CLASSES["Rabbit"](x_new=10, y_new=9)
    for i in range(ecosystem.capacity()):
        WILDLIFE_CLASSES["Rabbit"](x_new=20 + i % 20, y_new=20 + i // 20)
    eat = next(e for e in fox.effects if isinstance(e, EatObjectInFront))

    fox.hp = ecosystem.SATIATED_HP
    _face(fox, Rotations.UP)
    eat.run_effect(fox)
    assert rabbit.index in realm.OBJECT_LIST, "a full fox should not hunt"

    fox.hp = 30
    eat.run_effect(fox)
    assert rabbit.index not in realm.OBJECT_LIST
    assert fox.hp > 30


def test_find_nearest_sees_every_tile_of_the_ring(empty_world):
    empty_world(20)
    seeker = WILDLIFE_CLASSES["Rabbit"](x_new=10, y_new=10)
    for dx, dy in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
        target = WILDLIFE_CLASSES["Clover"](x_new=10 + dx, y_new=10 + dy)
        assert find_nearest(seeker, ["Clover"], rad=4) is target
        target.die()


class _DictRedis(dict):
    def set(self, key, value):
        self[key] = value


def test_world_map_and_species_plot_cover_all_types(empty_world, run_epochs):
    empty_world(30)
    main.populate_map_full(30)
    run_epochs(5)
    realm.REDIS_CONNECTION = _DictRedis()

    image_utils.generate_map()
    image_utils.get_plot_by_spicies(interval=1)

    assert realm.REDIS_CONNECTION["map_image"]
    assert realm.REDIS_CONNECTION["counts_historical_plot"]


def test_every_object_texture_is_sent_to_clients():
    textures = main.get_all_textures()
    missing = [t for t in OBJ_TYPE_LIST if obj_fut(t).image not in textures]
    assert not missing, f"textures not preloaded by the client: {missing}"


@pytest.mark.parametrize("food", ["Strawberry", "StrawberryRunner", "StrawberryPatch"])
def test_cow_and_calf_eat_strawberries(food):
    assert food in ecosystem.DIETS["Cow"]
    assert food in ecosystem.DIETS["Calf"]


def test_cow_grazes_most_plants():
    plant_types = {t for s in ecosystem.PLANT_SPECIES for t in ecosystem.SPECIES[s]}
    assert len(plant_types & set(ecosystem.DIETS["Cow"])) >= 0.75 * len(plant_types)


def test_player_cow_eats_without_ai_restrictions(empty_world):
    empty_world(20)
    cow = obj_fut("Cow")(x_new=10, y_new=10, is_player=True, player_name="hero")
    strawberry = WILDLIFE_CLASSES["Strawberry"](x_new=10, y_new=9)
    _face(cow, Rotations.UP)
    cow.hp = ecosystem.SATIATED_HP
    eat = next(e for e in cow.effects if isinstance(e, EatObjectInFront))

    assert not ecosystem.hunt_allowed("Strawberry")
    eat.run_effect(cow)
    assert strawberry.index not in realm.OBJECT_LIST
    assert cow.hp > ecosystem.SATIATED_HP
