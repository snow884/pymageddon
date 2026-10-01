import re
import sys

from type_defs.objects.wildlife_specs import new_type_names


def replace_with_html(text):
    # text = text.replace("**", "<b>")
    # text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"\n", "<br>", text)
    return text


OBJ_TYPE_LIST = list(
    dict.fromkeys(
        [
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
            "Mushroom2",
            "Spore",
            "Spore2",
            "Badger",
            "BadgerEgg",
            "Bee",
            "BeeEgg",
        ]
        + new_type_names()
    )
)

_TYPE_CACHE = {}


def obj_fut(str_in):

    if not isinstance(str_in, str):
        return str_in

    cls = _TYPE_CACHE.get(str_in)
    if cls is None:
        cls = _TYPE_CACHE[str_in] = _resolve_type(str_in)
    return cls


def _resolve_type(str_in):
    from type_defs.objects.wildlife import WILDLIFE_CLASSES

    if str_in in WILDLIFE_CLASSES:
        return WILDLIFE_CLASSES[str_in]

    if str_in == "Angel":
        if "Angel" not in sys.modules:
            from type_defs.objects.angel import Angel
        return Angel

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

    elif str_in == "Spore2":
        if "Spore2" not in sys.modules:
            from type_defs.objects.spore2 import Spore2
        return Spore2

    elif str_in == "Mushroom":
        if "Mushroom" not in sys.modules:
            from type_defs.objects.mushroom import Mushroom
        return Mushroom

    elif str_in == "Mushroom2":
        if "Mushroom2" not in sys.modules:
            from type_defs.objects.mushroom2 import Mushroom2
        return Mushroom2

    elif str_in == "Bee":
        if "Bee" not in sys.modules:
            from type_defs.objects.bee import Bee
        return Bee
    elif str_in == "BeeEgg":
        if "BeeEgg" not in sys.modules:
            from type_defs.objects.bee_egg import BeeEgg
        return BeeEgg

    else:
        raise Exception(f"class name {str_in} not found")


def get_types_dict():

    return {obj_str: obj_fut(obj_str) for obj_str in OBJ_TYPE_LIST}
