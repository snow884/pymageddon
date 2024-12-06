import json
import random
import time
from dataclasses import dataclass

import redis
from dataclasses_json import dataclass_json
from image_utils import generate_map
from type_defs.objects.base_object import BaseObject

r = redis.Redis(host="localhost", port=6379, db=0)


@dataclass
class Map:

    size_x: int = 0
    size_y: int = 0


@dataclass_json
@dataclass
class Player:
    name = ""


def find_nearest(obj: BaseObject, type_in, rad: int = 10):

    min_obj = None
    min_dist = -1
    min_i = -1
    min_j = -1

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):
            obj_index_found = TILES[(i, j)].occupied_by
            if obj_index_found:
                if type_in:

                    if isinstance(type_in, list):
                        obj_in_type = any(
                            [
                                isinstance(OBJECT_LIST[obj_index_found], t)
                                for t in type_in
                            ]
                        )
                    else:
                        obj_in_type = isinstance(OBJECT_LIST[obj_index_found], type_in)

                    if obj_in_type:
                        if (
                            min_dist > abs(obj.x - i) + abs(obj.y - j)
                        ) or min_dist == -1:
                            min_dist = abs(obj.x - i) + abs(obj.y - j)

                            min_i = i
                            min_j = j
                            min_obj = OBJECT_LIST[obj_index_found]
                else:

                    if (min_dist > abs(obj.x - i) + abs(obj.y - j)) or min_dist == -1:
                        min_dist = abs(obj.x - i) + abs(obj.y - j)

                        min_i = i
                        min_j = j
                        min_obj = OBJECT_LIST[obj_index_found]

    return min_obj


def find_objects(obj: BaseObject, rad: int = 30):

    objects_found = {}

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):
            obj_index_found = TILES[(i, j)].occupied_by

            if obj_index_found:

                objects_found[obj_index_found] = OBJECT_LIST[obj_index_found]

    return objects_found


def find_tiles(obj: BaseObject, rad: int = 30):

    tiles = {}

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):
            tiles[(i, j)] = TILES[(i, j)]

    return tiles


def find_particles(obj: BaseObject, rad: int = 30):

    particles_found = {}

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):

            particles_index_found = TILES[(i, j)].occupied_by_particles

            if particles_index_found:
                for particle_index_found in particles_index_found:

                    particles_found[particle_index_found] = PARTICLE_LIST[
                        particle_index_found
                    ]

    return particles_found


def get_nearest_free_location(x, y):

    rad = 1

    while rad < MAP.size_x:

        for i in [max(0, x - rad), min(x + rad, MAP.size_x)]:
            for j in range(max(0, y - rad), min(y + rad, MAP.size_x)):
                tile = TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        for i in range(max(0, x - rad), min(x + rad, MAP.size_x)):
            for j in [max(0, y - rad), min(y + rad, MAP.size_x)]:
                tile = TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        rad = rad + 1

    return None


def obj_fut(str):

    found = [
        inheritor
        for inheritor in BaseObject.__subclasses__()
        if str == inheritor.__name__
    ]

    if found:
        return found[0]
    else:
        raise Exception(f"class name {str} not found")


TILES = {}
OBJECT_LIST = {}
PLAYER_LIST = {}
PARTICLE_LIST = {}
OBJ_COUNTER = 0
MAP_VIEW_SIZE = 11
TIME_INTERVAL = 0.66
EPOCH_COUNTER = 0
MAP = Map(size_x=200, size_y=200)

for i in range(0, MAP.size_x):
    for j in range(0, MAP.size_y):
        TILES[(i, j)] = Tile1(x=i, y=j)
        if random.randint(0, 5) == 4:
            random.choice([Cow, Grass, Seed, Stone, Chicken, ChickenEgg, Fox])(
                x_new=i, y_new=j
            )

        else:

            if random.randint(0, 500) == 499:

                Angel(x_new=i, y_new=j)


def handle_players():

    global PLAYER_LIST

    for key in r.keys(pattern="player_*"):
        key_str = key.decode()

        player_name = key_str.replace("player_", "")

        if player_name not in PLAYER_LIST.keys():

            control_data_str = r.get(f"control_{player_name}")

            if control_data_str:

                control_data = json.loads(control_data_str)

                if any([value for key, value in control_data.items()]):
                    print(f"Creating player {player_name}")
                    x_new, y_new = get_nearest_free_location(10, 10)
                    Cow(
                        x_new=x_new,
                        y_new=y_new,
                        is_player=True,
                        player_name=player_name,
                    )


def evaluate_thinking():

    for i, obj in OBJECT_LIST.items():
        if not obj.is_player:
            obj.intent = obj.think()


def evaluate_moves():

    for i, obj in OBJECT_LIST.items():

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

    for player_name, player_object in PLAYER_LIST.items():

        # print(f"Sending maps for player {player_name}")

        map_data = r.get(f"map_{player_name}")

        objects = find_objects(player_object, rad=MAP_VIEW_SIZE)
        tiles = find_tiles(player_object, rad=MAP_VIEW_SIZE)
        particles = find_particles(player_object, rad=MAP_VIEW_SIZE)

        all_images = (
            [inheritor.image for inheritor in MyObject.__subclasses__()]
            + [inheritor.image for inheritor in Tile.__subclasses__()]
            + [inheritor.image for inheritor in Particle.__subclasses__()]
        )

        other_images = [
            "static/other/health_bar_green.png",
            "static/other/health_bar_red.png",
            "static/other/health_bar_yellow.png",
            "/static/other/map_image.png",
            "/static/other/red_cross.png",
        ]

        unix_timestamp = time.time()

        data = {
            "global_params": {
                "status": "running",
                "time_interval": TIME_INTERVAL,
                "map_view_size": MAP_VIEW_SIZE,
                "epoch": EPOCH_COUNTER,
                "textures": all_images + other_images,
                "timestamp": unix_timestamp,
                "new_map_timestamp": unix_timestamp + TIME_INTERVAL,
            },
            "player": {"object_id": player_object.index},
            "objects": {k: o.to_dict() for k, o in objects.items()},
            "tiles": {str(k): t.to_dict() for k, t in tiles.items()},
            "particles": {str(k): t.to_dict() for k, t in particles.items()},
        }

        r.set(f"map_{player_name}", json.dumps(data, cls=EnumEncoder))


def evaluate_player_control():

    for player_name, player_object in PLAYER_LIST.items():

        control_data_str = r.get(f"control_{player_name}")

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

        r.delete(f"control_{player_name}")


def evaluate_effects():

    for i, obj in list(OBJECT_LIST.items()):

        if i in OBJECT_LIST.keys():

            obj.effects()

    for i, par in list(PARTICLE_LIST.items()):

        if i in PARTICLE_LIST.keys():

            par.effects()


def count_object():

    cnt_dict = {}

    for i, o in OBJECT_LIST.items():
        cnt_dict[o.type_name] = cnt_dict.get(o.type_name, 0) + 1

    for type_name, cnt in cnt_dict.items():

        print(f"{type_name} : {cnt}")


while True:

    start_time = time.time()
    handle_players()
    evaluate_thinking()
    evaluate_player_control()
    evaluate_effects()
    evaluate_moves()
    count_object()
    send_map_data()
    generate_map(TILES, MAP, OBJECT_LIST)

    end_time = time.time()
    print(
        "The time of execution of above program is :",
        (end_time - start_time) * 10**3,
        "ms",
    )

    while (end_time - start_time) < TIME_INTERVAL:
        end_time = time.time()
        time.sleep(0.01)

    end_time = time.time()
    print("Total epoch time :", (end_time - start_time) * 10**3, "ms")

    EPOCH_COUNTER = EPOCH_COUNTER + 1
