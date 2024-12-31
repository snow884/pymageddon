import json
import random
import time

import redis

from common_utils.common_enums import Actions, EnumEncoder, Rotations
from common_utils.grid_utils import (
    find_objects,
    find_objects_location,
    find_particles,
    find_particles_location,
    find_tiles,
    find_tiles_location,
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
from type_defs.utils.utils import Map, Spectator

if realm.MODE == "full":
    realm.REDIS_CONNECTION = redis.Redis(host="localhost", port=6379, db=0)


def populate_map_full(sz=200):

    realm.MAP = Map(size_x=sz, size_y=sz)

    realm.SCORE_LIST = {"players": {}, "ranking": {}}

    for i in range(0, realm.MAP.size_x):
        for j in range(0, realm.MAP.size_y):
            realm.TILES[(i, j)] = Tile1(x=i, y=j)
            if random.randint(0, 10) == 9:
                random.choice([Cow, Grass, Seed, Stone, Chicken, ChickenEgg, Fox])(
                    x_new=i, y_new=j
                )

            else:

                if random.randint(0, 1000) == 999:

                    Angel(x_new=i, y_new=j)


def handle_players():

    for key in realm.REDIS_CONNECTION.keys(pattern="player_*"):
        key_str = key.decode()

        player_name = key_str.replace("player_", "")

        if player_name not in realm.PLAYER_LIST.keys():

            data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")

            if data_str:

                data = json.loads(data_str)

                if data["request_type"] == "player":

                    print(f"Creating player {player_name}")
                    x_new, y_new = get_nearest_free_location(
                        random.randint(0, realm.MAP.size_x - 1),
                        random.randint(0, realm.MAP.size_y - 1),
                    )
                    Cow(
                        x_new=x_new,
                        y_new=y_new,
                        is_player=True,
                        player_name=player_name,
                    )
                    realm.REDIS_CONNECTION.delete(f"game_{player_name}")

        if player_name not in realm.SPECTATOR_LIST.keys():

            data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")

            if data_str:

                data = json.loads(data_str)

                if data["request_type"] == "spectator":
                    spectator_follow_type = data["spectator_follow_type"]
                    spectator_follow_index = data["spectator_follow_index"]

                    obj = None

                    if spectator_follow_type == "object":
                        if spectator_follow_index in realm.OBJECT_LIST:
                            obj = realm.OBJECT_LIST[spectator_follow_index]
                        else:
                            print(
                                f"Cant find index {spectator_follow_index} for"
                                " spectator"
                            )

                    if spectator_follow_type == "tile":
                        if spectator_follow_index in realm.TILES:
                            obj = realm.TILES[spectator_follow_index]
                        else:
                            print(
                                f"Cant find index {spectator_follow_index} for"
                                " spectator"
                            )

                    if obj:
                        Spectator(player_name=player_name, obj=obj)

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


def find_all_types(obj):

    if isinstance(obj, BaseObject):
        objects = find_objects(obj, rad=realm.MAP_VIEW_SIZE)
        tiles = find_tiles(obj, rad=realm.MAP_VIEW_SIZE)
        particles = find_particles(obj, rad=realm.MAP_VIEW_SIZE)

    if isinstance(obj, BaseTile):

        objects = find_objects_location(obj.x, obj.y, rad=realm.MAP_VIEW_SIZE)
        tiles = find_tiles_location(obj.x, obj.y, rad=realm.MAP_VIEW_SIZE)
        particles = find_particles_location(obj.x, obj.y, rad=realm.MAP_VIEW_SIZE)

    return objects, tiles, particles


def send_map_data(
    player_object, player_name, large_message, object_type, objects, tiles, particles
):
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
        "../../static/other/joystick_center.png",
        "../../static/other/joystick_outside.png",
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
            "large_message": large_message,
        },
        "player": {"object_id": str(player_object.index), "object_type": object_type},
        "objects": {str(k): o.to_dict() for k, o in objects.items()},
        "tiles": {str(k): t.to_dict() for k, t in tiles.items()},
        "particles": {str(k): t.to_dict() for k, t in particles.items()},
    }

    realm.REDIS_CONNECTION.set(f"map_{player_name}", json.dumps(data, cls=EnumEncoder))
    realm.REDIS_CONNECTION.expire(f"map_{player_name}", 5)


def send_score_data(player_name):

    data = {
        "player_scores": realm.SCORE_LIST["players"].get(player_name, {}),
        "global_ranking": realm.SCORE_LIST["ranking"],
    }
    realm.REDIS_CONNECTION.set(
        f"score_{player_name}", json.dumps(data, cls=EnumEncoder)
    )


def send_map_data_all():

    for player_name, player_object in realm.PLAYER_LIST.items():

        objects, tiles, particles = find_all_types(player_object)

        send_map_data(
            player_object,
            player_object.player_name,
            None,
            "object",
            objects,
            tiles,
            particles,
        )

    for i, spectator in realm.SPECTATOR_LIST.items():
        objects, tiles, particles = find_all_types(spectator.obj)

        send_map_data(
            spectator.obj,
            spectator.player_name,
            spectator.large_message,
            spectator.object_type,
            objects,
            tiles,
            particles,
        )

    for player_name in list(
        set(realm.PLAYER_LIST.keys()).union(set(realm.SPECTATOR_LIST.keys()))
    ):

        send_score_data(player_name)


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

        # realm.REDIS_CONNECTION.delete(f"control_{player_name}")


def evaluate_effects():

    for i, obj in list(realm.OBJECT_LIST.items()):

        if i in realm.OBJECT_LIST.keys():
            if obj.effects:
                for e in obj.effects:
                    e.run_effect(obj)

            if obj.is_alive:

                if not obj.score:
                    obj.score = 0

                obj.score += 1

    for i, par in list(realm.PARTICLE_LIST.items()):

        if i in realm.PARTICLE_LIST.keys():

            par.effects()

    for i, spec in list(realm.SPECTATOR_LIST.items()):

        if i in realm.SPECTATOR_LIST.keys():

            spec.effects()


def count_object():

    cnt_dict = {}

    for i, o in realm.OBJECT_LIST.items():
        cnt_dict[o.type_name] = cnt_dict.get(o.type_name, 0) + 1

    for type_name, cnt in cnt_dict.items():

        print(f"{type_name} : {cnt}")


def generate_summary_yaml():

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


def main_loop(steps=None):

    if realm.MODE == "full":
        populate_map_full()
    else:
        populate_map_full(15)

    while True:

        start_time = time.time()
        handle_players()
        evaluate_thinking()

        if realm.MODE == "full":
            evaluate_player_control()

        evaluate_effects()
        evaluate_moves()
        if realm.MODE == "full":
            send_map_data_all()

        if realm.EPOCH_COUNTER % 20 == 0:
            count_object()
            generate_map()
            # generate_summary()

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

        if realm.EPOCH_COUNTER > steps:
            return


if __name__ == "__main__":
    main_loop()
