"""Food web and population regulation for the whole ecosystem.

Population control works like a logistic model with migration:
* every species (all development stages summed) has the same carrying
  capacity; births/seed emission are suppressed while a species is at capacity,
  so no species can take over the map;
* when a species drops below a small floor, an individual immigrates from
  outside the map (spawned at a random free tile), so no species dies out.
* consumers switch away from scarce food (prey switching): a species below
  ``SCARCITY_FRACTION`` of the capacity is neither chased nor eaten, which
  lets it recover while predators feed on abundant species instead.
* negative frequency dependence ("kill the winner"): a species cannot breed
  beyond ``DOMINANCE_RATIO`` times the mean species abundance, keeping all
  species at comparable numbers.
"""

import random

from singleton import realm
from type_defs.objects.wildlife_specs import (
    ANIMALS,
    CARNIVOROUS_FLOWER_PREY,
    EXISTING_ANIMAL_DIETS,
    PLANTS,
)

CAPACITY_PER_TILE = 0.006
MIN_CAPACITY = 8
FLOOR_FRACTION = 0.25
SCARCITY_FRACTION = 0.3
PLANT_SCARCITY_FRACTION = 0.25
RESCUE_INTERVAL = 5
DOMINANCE_RATIO = 1.25
BREED_MIN_HP = 60
BREED_HP_COST = 20
# Animals with at least this much hp are full and neither hunt nor eat.
SATIATED_HP = 90
FOOD_ENERGY_MULTIPLIER = 1.5

# Species -> development stages (type names), in life-cycle order.
SPECIES = {
    "Bee": ["BeeEgg", "Bee"],
    "Mushroom": ["Spore", "Mushroom"],
    "Mushroom2": ["Spore2", "Mushroom2"],
    "CarnivorousFlower": ["CarnivorousFlowerSeed", "CarnivorousFlower"],
}
for _name, _spec in ANIMALS.items():
    SPECIES[_name] = [s["name"] for s in _spec["stages"]]
for _name, _spec in PLANTS.items():
    SPECIES[_name] = [
        _spec[stage]["name"] for stage in ("seed", "sapling", "plant") if stage in _spec
    ]

SPECIES_OF_TYPE = {t: s for s, types in SPECIES.items() for t in types}

PLANT_SPECIES = {
    "Mushroom",
    "Mushroom2",
    "CarnivorousFlower",
} | set(PLANTS)

# Stage that immigrates when a species is rare. Spores die unless next to
# grass, so fungi immigrate as grown mushrooms.
RESCUE_TYPE = {s: types[0] for s, types in SPECIES.items()}
RESCUE_TYPE["Mushroom"] = "Mushroom"
RESCUE_TYPE["Mushroom2"] = "Mushroom2"

# Mobile type -> {eaten type: hp gained}.
DIETS = {}
for _name, _diet in EXISTING_ANIMAL_DIETS.items():
    DIETS[_name] = dict(_diet)
for _spec in ANIMALS.values():
    for _stage in _spec["stages"]:
        if _stage["kind"] in ("juvenile", "adult"):
            DIETS[_stage["name"]] = dict(_stage.get("diet", _spec["diet"]))
for _diet in DIETS.values():
    for _food in _diet:
        _diet[_food] = int(_diet[_food] * FOOD_ENERGY_MULTIPLIER)


def predators_of(type_name):
    """Types that hunt ``type_name``; used as the flee list of an animal."""
    hunters = sorted(t for t, diet in DIETS.items() if type_name in diet)
    if type_name in CARNIVOROUS_FLOWER_PREY:
        hunters.append("CarnivorousFlower")
    return hunters


def capacity():
    return max(
        MIN_CAPACITY, int(realm.MAP.size_x * realm.MAP.size_y * CAPACITY_PER_TILE)
    )


def floor():
    return max(1, int(capacity() * FLOOR_FRACTION))


def register_birth(type_name):
    realm.TYPE_COUNTS[type_name] = realm.TYPE_COUNTS.get(type_name, 0) + 1


def register_death(type_name):
    realm.TYPE_COUNTS[type_name] = realm.TYPE_COUNTS.get(type_name, 0) - 1


def species_count(species):
    return sum(realm.TYPE_COUNTS.get(t, 0) for t in SPECIES[species])


def species_counts():
    return {s: species_count(s) for s in SPECIES}


def species_limit(species):
    return realm.SPECIES_LIMITS.get(species, capacity())


def update_limits():
    counts = species_counts()
    mean = sum(counts.values()) / len(counts)
    limit = min(capacity(), max(2 * floor(), int(DOMINANCE_RATIO * mean)))
    realm.SPECIES_LIMITS = {s: limit for s in SPECIES}


def birth_allowed(type_name):
    species = SPECIES_OF_TYPE.get(type_name)
    if species is None or realm.MAP is None:
        return True
    return species_count(species) < species_limit(species)


def hunt_allowed(type_name):
    species = SPECIES_OF_TYPE.get(type_name)
    if species is None or realm.MAP is None:
        return True
    fraction = (
        PLANT_SCARCITY_FRACTION if species in PLANT_SPECIES else SCARCITY_FRACTION
    )
    return species_count(species) >= capacity() * fraction


def huntable(type_names):
    return [t for t in type_names if hunt_allowed(getattr(t, "type_name", t))]


def _random_free_tile(attempts=30):
    for _ in range(attempts):
        pos = (
            random.randrange(realm.MAP.size_x),
            random.randrange(realm.MAP.size_y),
        )
        if realm.TILES[pos].occupied_by is None:
            return pos
    return None


def rebalance():
    """Updates breeding limits and lets rare species immigrate."""
    update_limits()

    if realm.EPOCH_COUNTER % RESCUE_INTERVAL:
        return

    from common_utils.utils import obj_fut

    min_count = floor()
    for species in SPECIES:
        if species_count(species) >= min_count:
            continue
        pos = _random_free_tile()
        if pos is None:
            continue
        obj_fut(RESCUE_TYPE[species])(x_new=pos[0], y_new=pos[1])
        realm.IMMIGRATION_COUNTS[species] = realm.IMMIGRATION_COUNTS.get(species, 0) + 1
