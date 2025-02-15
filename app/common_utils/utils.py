import re
import sys


def replace_with_html(text):
    # text = text.replace("**", "<b>")
    # text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"\n", "<br>", text)
    return text


OBJ_TYPE_LIST = [
    "Angel",
    "Seed",
    "Seed2",
    "Seed3",
    "Grass",
    "Grass2",
    "Grass3",
    "Stone",
    "Stone2",
    "Chicken",
    "Cow",
    "Fox",
    "ChickenEgg",
    "CowEgg",
    "FoxEgg",
    "CarnivorousFlowerSeed",
    "CarnivorousFlower",
    "Mushroom",
    "Spore",
    "Badger",
    "BadgerEgg",
]


def obj_fut(str_in):

    if not isinstance(str_in, str):
        return str_in
    elif str_in == "Angel":
        if "Angel" not in sys.modules:
            from type_defs.objects.angel import Angel
        return Angel

    elif str_in == "Seed":
        if "Seed" not in sys.modules:
            from type_defs.objects.seed import Seed
        return Seed

    elif str_in == "Seed2":
        if "Seed2" not in sys.modules:
            from type_defs.objects.seed2 import Seed2
        return Seed2

    elif str_in == "Seed3":
        if "Seed3" not in sys.modules:
            from type_defs.objects.seed3 import Seed3
        return Seed3

    elif str_in == "Grass":
        if "Grass" not in sys.modules:
            from type_defs.objects.grass import Grass
        return Grass

    elif str_in == "Grass2":
        if "Grass2" not in sys.modules:
            from type_defs.objects.grass2 import Grass2
        return Grass2

    elif str_in == "Grass3":
        if "Grass" not in sys.modules:
            from type_defs.objects.grass3 import Grass3
        return Grass3

    elif str_in == "Stone":
        if "Stone" not in sys.modules:
            from type_defs.objects.stone import Stone
        return Stone

    elif str_in == "Stone2":
        if "Stone2" not in sys.modules:
            from type_defs.objects.stone2 import Stone2
        return Stone2

    elif str_in == "Chicken":
        if "Chicken" not in sys.modules:
            from type_defs.objects.chicken import Chicken
        return Chicken

    elif str_in == "Cow":
        if "Cow" not in sys.modules:
            from type_defs.objects.cow import Cow
        return Cow

    elif str_in == "Fox":
        if "Fox" not in sys.modules:
            from type_defs.objects.fox import Fox
        return Fox

    elif str_in == "ChickenEgg":
        if "ChickenEgg" not in sys.modules:
            from type_defs.objects.chicken_egg import ChickenEgg
        return ChickenEgg

    elif str_in == "CowEgg":
        if "CowEgg" not in sys.modules:
            from type_defs.objects.cow_egg import CowEgg
        return CowEgg

    elif str_in == "FoxEgg":
        if "FoxEgg" not in sys.modules:
            from type_defs.objects.fox_egg import FoxEgg
        return FoxEgg

    elif str_in == "CarnivorousFlowerSeed":
        if "CarnivorousFlowerSeed" not in sys.modules:
            from type_defs.objects.carnivorous_flower_seed import CarnivorousFlowerSeed
        return CarnivorousFlowerSeed

    elif str_in == "CarnivorousFlower":
        if "CarnivorousFlower" not in sys.modules:
            from type_defs.objects.carnivorous_flower import CarnivorousFlower
        return CarnivorousFlower

    elif str_in == "Spore":
        if "Spore" not in sys.modules:
            from type_defs.objects.spore import Spore
        return Spore

    elif str_in == "Mushroom":
        if "Mushroom" not in sys.modules:
            from type_defs.objects.mushroom import Mushroom
        return Mushroom

    elif str_in == "Badger":
        if "Badger" not in sys.modules:
            from type_defs.objects.badger import Badger
        return Badger
    elif str_in == "BadgerEgg":
        if "BadgerEgg" not in sys.modules:
            from type_defs.objects.badger_egg import BadgerEgg
        return BadgerEgg

    else:
        raise Exception(f"class name {str_in} not found")


def get_types_dict():

    return {obj_str: obj_fut(obj_str) for obj_str in OBJ_TYPE_LIST}
