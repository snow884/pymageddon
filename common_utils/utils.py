import sys


def obj_fut(str_in):

    if not isinstance(str_in, str):
        return str_in

    elif str_in == "Seed":
        if "Seed" not in sys.modules:
            from type_defs.objects.seed import Seed
        return Seed

    elif str_in == "Grass":
        if "Grass" not in sys.modules:
            from type_defs.objects.grass import Grass
        return Grass

    elif str_in == "Stone":
        if "Stone" not in sys.modules:
            from type_defs.objects.stone import Stone
        return Stone

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

    else:
        raise Exception(f"class name {str_in} not found")
