"""Builds the object classes for every species described in ``wildlife_specs``."""

import random

from common_utils.common_enums import Rotations
from common_utils.ecosystem import BREED_HP_COST, BREED_MIN_HP, DIETS, predators_of
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.emit_object import EmitObject
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.objects.effects.turn_into import TurnInto
from type_defs.objects.wildlife_specs import (
    ANIMALS,
    EXISTING_ANIMAL_JUVENILES,
    INANIMATE,
    PLANTS,
)
from type_defs.particles.blood_mark_particle import BlookMarkParticle
from type_defs.particles.death_particle import DeathParticle
from type_defs.particles.track_particle import TrackParticle

WILDLIFE_CLASSES = {}

# Types placed on the map when the world is generated.
POPULATE_TYPES = []


class _Wildlife:
    description = ""

    def __init__(
        self,
        x_new: int,
        y_new: int,
        is_player=False,
        player_name=None,
        code: str = None,
        code_store: str = None,
        family_name: str = None,
        variables=None,
    ):
        BaseObject.__init__(
            self,
            x_new=x_new,
            y_new=y_new,
            is_player=is_player,
            player_name=player_name,
            code=code,
            # Juveniles pass their bot code on when they grow up.
            code_store=code_store or code,
            family_name=family_name,
            variables=variables,
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def get_description_short(self) -> str:
        return self.description


class _MobileWildlife(_Wildlife):
    is_alive = True
    speed = 1.0
    chase_after = ()
    chase_from = ()

    def think(self):
        if self.code:
            return BaseObject.think(self)
        if self.speed < 1.0 and random.random() > self.speed:
            return None
        return simple_chase(
            self, chase_after=self.chase_after, chase_from=self.chase_from
        )

    def move_to_position(self, x_new: int, y_new: int):
        x_old, y_old = self.x, self.y
        res = BaseObject.move_to_position(self, x_new, y_new)
        if res:
            TrackParticle(x_old, y_old, rotation=self.rotation)
        return res

    def die(self, player_afterlife=True):
        DeathParticle(x_new=self.x, y_new=self.y)
        BlookMarkParticle(x_new=self.x, y_new=self.y)
        BaseObject.die(self, player_afterlife)


def _register(name, base, attrs):
    # Direct BaseObject subclasses are picked up by the texture preloader.
    cls = type(name, (base, BaseObject), {"__module__": __name__, **attrs})
    WILDLIFE_CLASSES[name] = cls
    globals()[name] = cls
    return cls


def _common_attrs(name, image, desc, rgb):
    return {
        "type_name": name,
        "image": f"../../static/objects/{image}.png",
        "description": desc,
        "rgb_map": tuple(rgb),
    }


def _mobile_attrs(name, speed):
    return {
        "speed": speed,
        "chase_after": tuple(DIETS[name]),
        "chase_from": tuple(predators_of(name)),
    }


for _species, _juv in EXISTING_ANIMAL_JUVENILES.items():
    _register(
        _juv["name"],
        _MobileWildlife,
        {
            **_common_attrs(_juv["name"], _juv["image"], _juv["desc"], _juv["rgb"]),
            **_mobile_attrs(_juv["name"], 1.0),
            "effects": [
                EatObjectInFront(types_eaten_to_hp_conv=DIETS[_juv["name"]]),
                HpDepletion(skip_cycles=_juv["hp_skip"]),
                TurnInto(future_object_class=_species, time_to_turn=_juv["grow_time"]),
            ],
        },
    )


for _species, _spec in ANIMALS.items():
    _stages = _spec["stages"]
    for _i, _stage in enumerate(_stages):
        _name, _kind = _stage["name"], _stage["kind"]
        _attrs = _common_attrs(_name, _stage["image"], _stage["desc"], _spec["rgb"])
        _next = _stages[_i + 1]["name"] if _i + 1 < len(_stages) else None

        if _kind == "egg":
            _attrs["effects"] = [
                TurnInto(future_object_class=_next, time_to_turn=_spec["hatch_time"])
            ]
            _register(_name, _Wildlife, _attrs)
        elif _kind == "pupa":
            _attrs["effects"] = [
                TurnInto(future_object_class=_next, time_to_turn=_spec["pupa_time"])
            ]
            _register(_name, _Wildlife, _attrs)
        elif _kind == "juvenile":
            _attrs.update(_mobile_attrs(_name, _stage.get("speed", _spec["speed"])))
            _attrs["effects"] = [
                EatObjectInFront(types_eaten_to_hp_conv=DIETS[_name]),
                HpDepletion(skip_cycles=_spec["hp_skip"]),
                TurnInto(future_object_class=_next, time_to_turn=_spec["grow_time"]),
            ]
            _register(_name, _MobileWildlife, _attrs)
        else:
            _attrs.update(_mobile_attrs(_name, _stage.get("speed", _spec["speed"])))
            _attrs["effects"] = [
                EatObjectInFront(types_eaten_to_hp_conv=DIETS[_name]),
                HpDepletion(skip_cycles=_spec["hp_skip"]),
                LayObject(
                    object_to_lay=_stages[0]["name"],
                    time_to_lay=_spec["lay_time"],
                    min_hp=_spec.get("breed_hp", BREED_MIN_HP),
                    hp_cost=_spec.get("breed_cost", BREED_HP_COST),
                ),
            ]
            _register(_name, _MobileWildlife, _attrs)
            POPULATE_TYPES.append(_name)


for _species, _spec in PLANTS.items():
    _seed, _plant = _spec["seed"], _spec["plant"]
    _sapling = _spec.get("sapling")
    _register(
        _seed["name"],
        _Wildlife,
        {
            **_common_attrs(_seed["name"], _seed["image"], _seed["desc"], _spec["rgb"]),
            "effects": [
                TurnInto(
                    future_object_class=(_sapling or _plant)["name"],
                    time_to_turn=_spec["sprout_time"],
                )
            ],
        },
    )
    if _sapling:
        _register(
            _sapling["name"],
            _Wildlife,
            {
                **_common_attrs(
                    _sapling["name"], _sapling["image"], _sapling["desc"], _spec["rgb"]
                ),
                "effects": [
                    TurnInto(
                        future_object_class=_plant["name"],
                        time_to_turn=_spec["grow_time"],
                    )
                ],
            },
        )
    _register(
        _plant["name"],
        _Wildlife,
        {
            **_common_attrs(
                _plant["name"], _plant["image"], _plant["desc"], _spec["rgb"]
            ),
            "effects": [
                EmitObject(
                    object_to_emit=_seed["name"], time_to_emit=_spec["emit_time"]
                ),
                HpDepletion(skip_cycles=_spec["lifespan_skip"]),
            ],
        },
    )
    POPULATE_TYPES.append(_plant["name"])


for _name, _spec in INANIMATE.items():
    _register(
        _name,
        _Wildlife,
        {
            **_common_attrs(_name, _spec["image"], _spec["desc"], _spec["rgb"]),
            "effects": None,
        },
    )
    POPULATE_TYPES.append(_name)
