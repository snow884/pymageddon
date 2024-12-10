import json
import random
import time
from dataclasses import dataclass

import redis
from dataclasses_json import dataclass_json

from common_utils.common_enums import Actions, EnumEncoder, Rotations
from common_utils.grid_utils import (
    find_objects,
    find_particles,
    find_tiles,
    get_nearest_free_location,
)
from common_utils.image_utils import generate_map
from singleton import realm
from type_defs.objects.angel import Angel
from type_defs.objects.base_object import BaseObject
from type_defs.objects.chicken import Chicken
from type_defs.objects.chicken_egg import ChickenEgg
from type_defs.objects.cow import Cow
from type_defs.objects.fox import Fox
from type_defs.objects.grass import Grass
from type_defs.objects.seed import Seed
from type_defs.objects.stone import Stone
from type_defs.particles.base_particle import BaseParticle
from type_defs.tiles.base_tile import BaseTile
from type_defs.tiles.tile1 import Tile1

realm.REDIS_CONNECTION = redis.Redis(host="localhost", port=6379, db=0)


@dataclass
class Map:

    size_x: int = 0
    size_y: int = 0


@dataclass_json
@dataclass
class Player:
    name = ""


realm.MAP = Map(size_x=200, size_y=200)


def populate_map():

    for i in range(0, realm.MAP.size_x):
        for j in range(0, realm.MAP.size_y):
            realm.TILES[(i, j)] = Tile1(x=i, y=j)
            if random.randint(0, 5) == 4:
                random.choice([Cow, Grass, Seed, Stone, Chicken, ChickenEgg, Fox])(
                    x_new=i, y_new=j
                )

            else:

                if random.randint(0, 500) == 499:

                    Angel(x_new=i, y_new=j)


def handle_players():

    for key in realm.REDIS_CONNECTION.keys(pattern="player_*"):
        key_str = key.decode()

        player_name = key_str.replace("player_", "")
        print(player_name)
        print(realm.PLAYER_LIST.keys())

        if player_name not in realm.PLAYER_LIST.keys():

            status_b = realm.REDIS_CONNECTION.get(f"game_{player_name}")
            if status_b:
                status = status_b.decode()

                if status == "request_play":

                    print(f"Creating player {player_name}")
                    x_new, y_new = get_nearest_free_location(
                        random.randint(0, realm.MAP.size_x),
                        random.randint(0, realm.MAP.size_y),
                    )
                    Cow(
                        x_new=x_new,
                        y_new=y_new,
                        is_player=True,
                        player_name=player_name,
                    )
                    realm.REDIS_CONNECTION.delete(f"game_{player_name}")


def evaluate_thinking():

    for i, obj in realm.OBJECT_LIST.items():
        if not obj.is_player:
            obj.intent = obj.think()


def evaluate_moves():

    for i, obj in realm.OBJECT_LIST.items():

        if obj.intent == Actions.MOVE_FORWARD:

            x_new = obj.x
            y_new = obj.y

            if obj.rotation == Rotations.UP:

                y_new = obj.y - 1

            elif obj.rotation == Rotations.RIGHT:

                x_new = obj.x + 1

            elif obj.rotation == Rotations.DOWN:

                y_new = obj.y + 1

            elif obj.rotation == Rotations.LEFT:

                x_new = obj.x - 1

            success = obj.move_to_position(x_new, y_new)

            # if success:

            #     print(f"Moving {obj} to position ({x_new}, {y_new})")
            # else:

            #     print(f"Can't move {obj} to position ({x_new}, {y_new})")

        if obj.intent in [
            Actions.ROTATE_DOWN,
            Actions.ROTATE_UP,
            Actions.ROTATE_RIGHT,
            Actions.ROTATE_LEFT,
        ]:

            if obj.intent == Actions.ROTATE_DOWN:
                obj.rotation = Rotations.DOWN
            elif obj.intent == Actions.ROTATE_UP:
                obj.rotation = Rotations.UP
            elif obj.intent == Actions.ROTATE_RIGHT:
                obj.rotation = Rotations.RIGHT
            elif obj.intent == Actions.ROTATE_LEFT:
                obj.rotation = Rotations.LEFT

            # print(f"Rotating {obj} to rotation {obj.intent}")


def send_map_data():

    for player_name, player_object in realm.PLAYER_LIST.items():

        objects = find_objects(player_object, rad=realm.MAP_VIEW_SIZE)
        tiles = find_tiles(player_object, rad=realm.MAP_VIEW_SIZE)
        particles = find_particles(player_object, rad=realm.MAP_VIEW_SIZE)

        all_images = (
            [inheritor.image for inheritor in BaseObject.__subclasses__()]
            + [inheritor.image for inheritor in BaseTile.__subclasses__()]
            + [inheritor.image for inheritor in BaseParticle.__subclasses__()]
        )

        other_images = [
            "../../static/other/health_bar_green.png",
            "../../static/other/health_bar_red.png",
            "../../static/other/health_bar_yellow.png",
            "../../static/other/map_image.png",
            "../../static/other/red_cross.png",
        ]

        unix_timestamp = time.time()

        data = {
            "global_params": {
                "status": "running",
                "time_interval": realm.TIME_INTERVAL,
                "map_view_size": realm.MAP_VIEW_SIZE,
                "epoch": realm.EPOCH_COUNTER,
                "textures": all_images + other_images,
                "timestamp": unix_timestamp,
                "new_map_timestamp": unix_timestamp + realm.TIME_INTERVAL,
            },
            "player": {"object_id": str(player_object.index)},
            "objects": {str(k): o.to_dict() for k, o in objects.items()},
            "tiles": {str(k): t.to_dict() for k, t in tiles.items()},
            "particles": {str(k): t.to_dict() for k, t in particles.items()},
        }

        realm.REDIS_CONNECTION.set(
            f"map_{player_name}", json.dumps(data, cls=EnumEncoder)
        )


def evaluate_player_control():

    for player_name, player_object in realm.PLAYER_LIST.items():

        control_data_str = realm.REDIS_CONNECTION.get(f"control_{player_name}")

        if not control_data_str:
            player_object.intent = None
            continue

        control_data = json.loads(control_data_str)

        if control_data["ArrowDown"]:
            if player_object.rotation == Rotations.DOWN:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_DOWN
        elif control_data["ArrowUp"]:
            if player_object.rotation == Rotations.UP:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_UP
        elif control_data["ArrowRight"]:
            if player_object.rotation == Rotations.RIGHT:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_RIGHT
        elif control_data["ArrowLeft"]:
            if player_object.rotation == Rotations.LEFT:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_LEFT
        else:
            player_object.intent = None

        realm.REDIS_CONNECTION.delete(f"control_{player_name}")


def evaluate_effects():

    for i, obj in list(realm.OBJECT_LIST.items()):

        if i in realm.OBJECT_LIST.keys():
            if obj.effects:
                for e in obj.effects:
                    e.run_effect(obj)

    for i, par in list(realm.PARTICLE_LIST.items()):

        if i in realm.PARTICLE_LIST.keys():

            par.effects()


def count_object():

    cnt_dict = {}

    for i, o in realm.OBJECT_LIST.items():
        cnt_dict[o.type_name] = cnt_dict.get(o.type_name, 0) + 1

    for type_name, cnt in cnt_dict.items():

        print(f"{type_name} : {cnt}")


def generate_summary():

    summary_json = {}

    for i, o in realm.OBJECT_LIST.items():

        if o.type_name not in summary_json.keys():
            summary_json[o.type_name] = {}
            summary_json[o.type_name]["type_name"] = o.type_name
            summary_json[o.type_name]["image"] = o.image
            summary_json[o.type_name]["effects"] = (
                [e.description() for e in o.effects] if o.effects else []
            )
            summary_json[o.type_name]["description"] = ""
            summary_json[o.type_name]["families"] = {}

        if o.family_index not in summary_json[o.type_name]["families"].keys():
            summary_json[o.type_name]["families"][o.family_index] = {}
            summary_json[o.type_name]["families"][o.family_index]["family_name"] = ""
            summary_json[o.type_name]["families"][o.family_index]["image"] = o.image
            summary_json[o.type_name]["families"][o.family_index]["effects"] = (
                [e.description() for e in o.effects] if o.effects else []
            )
            summary_json[o.type_name]["families"][o.family_index]["description"] = ""
            summary_json[o.type_name]["families"][o.family_index]["code"] = o.code
            summary_json[o.type_name]["families"][o.family_index]["objects"] = {}

        if (
            o.index
            not in summary_json[o.type_name]["families"][o.family_index]["objects"]
        ):
            summary_json[o.type_name]["families"][o.family_index]["objects"][
                o.index
            ] = o.index

    with open("objects_summary.json", "w") as f:
        s = json.dumps(summary_json, cls=EnumEncoder)
        f.write(s)


def main_loop():

    populate_map()

    while True:

        start_time = time.time()
        handle_players()
        evaluate_thinking()
        evaluate_player_control()
        evaluate_effects()
        evaluate_moves()
        count_object()
        send_map_data()

        if realm.EPOCH_COUNTER % 20:
            generate_map()
            generate_summary()

        end_time = time.time()
        print(
            "The time of execution of above program is :",
            (end_time - start_time) * 10**3,
            "ms",
        )

        while (end_time - start_time) < realm.TIME_INTERVAL:
            end_time = time.time()
            time.sleep(0.01)

        end_time = time.time()
        print("Total epoch time :", (end_time - start_time) * 10**3, "ms")

        realm.EPOCH_COUNTER = realm.EPOCH_COUNTER + 1


if __name__ == "__main__":
    main_loop()
