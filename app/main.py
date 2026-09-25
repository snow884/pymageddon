import json
import queue
import random
import threading
import time

import cython
import redis
from common_utils.backup_utils import backup_to_s3, restore_from_s3
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
from common_utils.image_utils import (
    generate_map,
    get_plot_by_spicies,
    get_refresh_time_plot,
)
from singleton import realm
from type_defs.objects.angel import Angel
from type_defs.objects.badger import Badger
from type_defs.objects.badger_egg import BadgerEgg
from type_defs.objects.base_object import BaseObject
from type_defs.objects.bee import Bee
from type_defs.objects.bee_egg import BeeEgg
from type_defs.objects.chicken import Chicken
from type_defs.objects.chicken_egg import ChickenEgg
from type_defs.objects.cow import Cow
from type_defs.objects.fox import Fox
from type_defs.objects.grass import Grass
from type_defs.objects.grass2 import Grass2
from type_defs.objects.grass3 import Grass3
from type_defs.objects.mushroom import Mushroom
from type_defs.objects.mushroom2 import Mushroom2
from type_defs.objects.seed import Seed
from type_defs.objects.seed2 import Seed2
from type_defs.objects.seed3 import Seed3
from type_defs.objects.spore import Spore
from type_defs.objects.stone import Stone
from type_defs.objects.stone2 import Stone2
from type_defs.particles.base_particle import BaseParticle
from type_defs.tiles.base_tile import BaseTile
from type_defs.tiles.tile1 import Tile1
from type_defs.utils.utils import Map, Spectator

if realm.MODE == "full":
    realm.REDIS_CONNECTION = redis.Redis(
        host="pymageddon-redis-server", port=6379, db=0
    )


def populate_map_full(sz=100):

    realm.MAP = Map(size_x=sz, size_y=sz)

    realm.SCORE_LIST = {"players": {}, "ranking": {}}

    for i in range(0, realm.MAP.size_x):
        for j in range(0, realm.MAP.size_y):
            realm.TILES[(i, j)] = Tile1(x=i, y=j)
            if random.randint(0, 10) == 9:
                random.choice(
                    [
                        Cow,
                        Grass,
                        Grass2,
                        Grass3,
                        Seed,
                        Seed2,
                        Seed3,
                        Stone,
                        Stone2,
                        Chicken,
                        ChickenEgg,
                        Fox,
                        Spore,
                        Mushroom,
                        Mushroom2,
                        Badger,
                        BadgerEgg,
                        Bee,
                        BeeEgg,
                        # Seed,
                        # CarnivorousFlower,
                    ]
                )(x_new=i, y_new=j)

            else:

                if random.randint(0, 1000) == 999:

                    Angel(x_new=i, y_new=j)


_CACHED_TEXTURES = None


def get_all_textures():
    global _CACHED_TEXTURES
    if _CACHED_TEXTURES is None:
        all_images = (
            [inheritor.image for inheritor in BaseObject.__subclasses__()]
            + [inheritor.image for inheritor in BaseTile.__subclasses__()]
            + [inheritor.image for inheritor in BaseParticle.__subclasses__()]
        )
        other_images = [
            "../../static/other/health_bar_green.png",
            "../../static/other/health_bar_red.png",
            "../../static/other/health_bar_yellow.png",
            "../../static/other/circle.png",
            "../../map_image.png",
            "../../static/other/red_cross.png",
            "../../static/other/joystick_center.png",
            "../../static/other/joystick_outside.png",
            "../../static/other/exit_button.png",
        ]
        _CACHED_TEXTURES = all_images + other_images
    return _CACHED_TEXTURES


def handle_players():
    player_keys = (
        list(realm.REDIS_CONNECTION.scan_iter(match="player_*"))
        if hasattr(realm.REDIS_CONNECTION, "scan_iter")
        else realm.REDIS_CONNECTION.keys(pattern="player_*")
    )

    for key in player_keys:
        key_str = key.decode() if isinstance(key, bytes) else str(key)

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
        else:
            data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")

            if data_str:

                data = json.loads(data_str)

                if data["request_type"] == "end_game":

                    player_object = realm.PLAYER_LIST[player_name]

                    player_object.die(player_afterlife=False)

                    realm.REDIS_CONNECTION.delete(f"game_{player_name}")

        if player_name not in [s.player_name for i, s in realm.SPECTATOR_LIST.items()]:

            data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")

            if data_str:

                data = json.loads(data_str)
                print(data)

                if data["request_type"] == "spectator":
                    spectator_follow_type = data["spectator_follow_type"]
                    spectator_follow_index = data.get("spectator_follow_index")

                    obj = None

                    if spectator_follow_type == "object":

                        if spectator_follow_index in realm.OBJECT_LIST:
                            obj = realm.OBJECT_LIST[spectator_follow_index]
                        else:
                            if "code" in data:

                                code = data["code"]

                                x_new, y_new = get_nearest_free_location(
                                    random.randint(0, realm.MAP.size_x - 1),
                                    random.randint(0, realm.MAP.size_y - 1),
                                )

                                obj = Cow(
                                    x_new=x_new,
                                    y_new=y_new,
                                    is_player=False,
                                    player_name=player_name,
                                    family_name=player_name,
                                    code=code,
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
                        Spectator(
                            obj=obj,
                            player_name=player_name,
                            object_type="object",
                            lifetime=1000,
                            title_indicative_message="Following bot",
                        )
                        realm.REDIS_CONNECTION.delete(f"game_{player_name}")
        else:

            data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")

            if data_str:

                data = json.loads(data_str)

                if data["request_type"] == "end_game":

                    spectator = {
                        s.player_name: s for i, s in realm.SPECTATOR_LIST.items()
                    }[player_name]

                    spectator.die()

                    realm.REDIS_CONNECTION.delete(f"game_{player_name}")

        data_str = realm.REDIS_CONNECTION.get(f"game_{player_name}")
        if data_str:
            data = json.loads(data_str)
            print(f"Cant process data {data}, deleting...")
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
    player_object,
    player_name,
    large_message,
    title_indicative_message,
    object_type,
    objects,
    tiles,
    particles,
):
    unix_timestamp = time.time()

    if object_type == "object":
        if player_object.is_player or player_object.code:
            dashboard_message = f"Score: {player_object.score}"
        else:
            dashboard_message = ""

        dashboard_message += "\n" + f"Iter. time: {int(realm.LAST_REFRESH_TIME)} ms"

        if player_object.code:
            vars_str = "\n".join(
                [f"{k}={v}" for k, v in player_object.variables.items()][:10]
            )
            dashboard_message += "\n" + vars_str

    else:
        dashboard_message = ""

    data = {
        "global_params": {
            "status": "running",
            "time_interval": realm.TIME_INTERVAL,
            "map_view_size": realm.MAP_VIEW_SIZE,
            "map_size_x": realm.MAP.size_x,
            "epoch": realm.EPOCH_COUNTER,
            "textures": get_all_textures(),
            "timestamp": unix_timestamp,
            "new_map_timestamp": unix_timestamp + realm.TIME_INTERVAL,
            "large_message": large_message,
            "title_indicative_message": title_indicative_message,
            "dashboard_message": dashboard_message,
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

    with realm.LOCK:
        for player_name, player_object in realm.PLAYER_LIST.items():

            objects, tiles, particles = find_all_types(player_object)

            send_map_data(
                player_object,
                player_object.player_name,
                None,
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
                spectator.title_indicative_message,
                spectator.object_type,
                objects,
                tiles,
                particles,
            )

    player_keys = (
        list(realm.REDIS_CONNECTION.scan_iter(match="player_*"))
        if hasattr(realm.REDIS_CONNECTION, "scan_iter")
        else realm.REDIS_CONNECTION.keys(pattern="player_*")
    )

    for key in player_keys:
        key_str = key.decode() if isinstance(key, bytes) else str(key)

        player_name = key_str.replace("player_", "")

        send_score_data(player_name)


def evaluate_player_control():

    for player_name, player_object in realm.PLAYER_LIST.items():

        control_data_str = realm.REDIS_CONNECTION.get(f"control_{player_name}")

        if not control_data_str:
            player_object.intent = None
            continue

        control_data = json.loads(control_data_str)

        if control_data.get("ArrowDown"):
            if player_object.rotation == Rotations.DOWN:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_DOWN
        elif control_data.get("ArrowUp"):
            if player_object.rotation == Rotations.UP:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_UP
        elif control_data.get("ArrowRight"):
            if player_object.rotation == Rotations.RIGHT:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_RIGHT
        elif control_data.get("ArrowLeft"):
            if player_object.rotation == Rotations.LEFT:
                player_object.intent = Actions.MOVE_FORWARD
            else:
                player_object.intent = Actions.ROTATE_LEFT
        else:
            player_object.intent = None


def evaluate_effects():

    for i, obj in list(realm.OBJECT_LIST.items()):

        if i in realm.OBJECT_LIST.keys():
            if obj.effects:
                obj.run_effects()

            if obj.is_alive:

                if not obj.score:
                    obj.score = 0

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

        if not summary_json.get(o.type_name):
            summary_json[o.type_name] = {}

        summary_json[o.type_name]["type_name"] = o.type_name
        summary_json[o.type_name]["image"] = o.image
        summary_json[o.type_name]["hp"] = o.hp
        summary_json[o.type_name]["total_objects"] = (
            summary_json[o.type_name].get("total_objects", 0) + 1
        )
        summary_json[o.type_name]["rgb_map"] = str(o.rgb_map)
        summary_json[o.type_name]["effects"] = (
            [
                {"description": e.description(), "effect_name": e.effect_name}
                for e in o.effects
            ]
            if o.effects
            else []
        )
        summary_json[o.type_name]["description_long"] = o.get_description_long()
        summary_json[o.type_name]["description_short"] = o.get_description_short()

        if not summary_json[o.type_name].get("objects"):
            summary_json[o.type_name]["objects"] = {}

        summary_json[o.type_name]["objects"][o.index] = {
            "hp": o.hp,
            "score": o.score,
            "player_name": o.player_name,
            "family_name": o.family_name,
            "code_sha1": o.code_sha1,
            "code": o.code,
        }

        if not summary_json[o.type_name].get("families"):
            summary_json[o.type_name]["families"] = {}

        if o.code:

            if not summary_json[o.type_name]["families"].get(o.family_name):
                summary_json[o.type_name]["families"][o.family_name] = {}

            if not summary_json[o.type_name]["families"][o.family_name].get(
                o.code_sha1
            ):
                summary_json[o.type_name]["families"][o.family_name][o.code_sha1] = {
                    "code_sha1": o.code_sha1,
                    "code": o.code,
                    "object_index_list": [],
                }

            summary_json[o.type_name]["families"][o.family_name][o.code_sha1][
                "object_index_list"
            ].append(o.index)

            print(summary_json[o.type_name]["families"])

        # if o.family_index not in summary_json[o.type_name]["families"].keys():
        #     summary_json[o.type_name]["families"][o.family_index] = {}
        #     summary_json[o.type_name]["families"][o.family_index]["family_name"] = ""
        #     summary_json[o.type_name]["families"][o.family_index]["image"] = o.image
        #     summary_json[o.type_name]["families"][o.family_index]["effects"] = (
        #         [e.description() for e in o.effects] if o.effects else []
        #     )
        #     summary_json[o.type_name]["families"][o.family_index]["description"] = ""
        #     summary_json[o.type_name]["families"][o.family_index]["code"] = o.code
        #     summary_json[o.type_name]["families"][o.family_index]["objects"] = {}

        # if (
        #     o.index
        #     not in summary_json[o.type_name]["families"][o.family_index]["objects"]
        # ):
        #     summary_json[o.type_name]["families"][o.family_index]["objects"][
        #         o.index
        #     ] = o.index

    realm.REDIS_CONNECTION.set(
        f"all_objects_summary", json.dumps(summary_json, cls=EnumEncoder)
    )


def worker_send_map_data_all(q, thread_id):
    while True:
        try:
            item = q.get(
                timeout=realm.TIME_INTERVAL * 2
            )  # Block until an item is available or timeout
            print(f"Thread {thread_id}: Processing {item}")
            send_map_data_all()
            q.task_done()  # Indicate that a formerly enqueued task is complete
        except queue.Empty as e:
            print(f"Thread {thread_id}: queue is empty")
        except Exception as e:
            print(f"Thread {thread_id}: got exception: {e}")


def worker_generate_plots(q, thread_id):
    while True:
        try:
            item = q.get(
                timeout=realm.TIME_INTERVAL * 30 * 2
            )  # Block until an item is available or timeout
            print(f"Thread {thread_id}: Processing {item}")

            with realm.LOCK:
                generate_map()

                get_plot_by_spicies(interval=30)
                get_refresh_time_plot(interval=30)

                generate_summary_yaml()

            q.task_done()  # Indicate that a formerly enqueued task is complete
        except queue.Empty as e:
            print(f"Thread {thread_id}: queue is empty")
        except Exception as e:
            print(f"Thread {thread_id}: got exception: {e}")


def worker_backup_redis(q, thread_id):
    while True:
        try:
            item = q.get(
                timeout=realm.TIME_INTERVAL * int(360 / realm.TIME_INTERVAL) * 2
            )  # Block until an item is available or timeout
            print(f"Thread {thread_id}: Processing {item}")

            backup_to_s3()

            q.task_done()  # Indicate that a formerly enqueued task is complete
        except queue.Empty as e:
            print(f"Thread {thread_id}: queue is empty")
        except Exception as e:
            print(f"Thread {thread_id}: got exception: {e}")


def main_loop(steps=None):

    if cython.compiled:
        print("Compiled with cython")
    else:
        print("NOT Compiled with cython")

    if realm.MODE == "full":
        populate_map_full()
    else:
        populate_map_full(15)

    threads = []

    q_send_map_data_all = queue.Queue()
    thread_send_map_data_all = threading.Thread(
        target=worker_send_map_data_all,
        args=(q_send_map_data_all, "thread_send_map_data_all"),
        daemon=True,
    )
    thread_send_map_data_all.start()
    threads.append(thread_send_map_data_all)

    q_generate_plots = queue.Queue()
    thread_generate_plots = threading.Thread(
        target=worker_generate_plots,
        args=(q_generate_plots, "thread_generate_plots"),
        daemon=True,
    )
    thread_generate_plots.start()
    threads.append(thread_generate_plots)

    q_backup_redis = queue.Queue()
    thread_backup_redis = threading.Thread(
        target=worker_backup_redis,
        args=(q_backup_redis, "thread_backup_redis"),
        daemon=True,
    )
    thread_backup_redis.start()
    threads.append(thread_backup_redis)

    while True:

        start_time = time.time()
        with realm.LOCK:
            handle_players()
            evaluate_thinking()

            if realm.MODE == "full":
                evaluate_player_control()

            evaluate_effects()
            evaluate_moves()

        if realm.MODE == "full":
            q_send_map_data_all.put(realm.EPOCH_COUNTER)

            if realm.EPOCH_COUNTER % 30 == 0:
                q_generate_plots.put(realm.EPOCH_COUNTER)

            if realm.EPOCH_COUNTER % int(360 / realm.TIME_INTERVAL) == 0:
                q_backup_redis.put(realm.EPOCH_COUNTER)

        end_time = time.time()
        realm.LAST_REFRESH_TIME = (end_time - start_time) * 10**3
        print(
            "The time of execution of above program is :",
            realm.LAST_REFRESH_TIME,
            "ms",
        )

        sleep_time = realm.TIME_INTERVAL - (end_time - start_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

        end_time = time.time()
        print("Total epoch time :", (end_time - start_time) * 10**3, "ms")

        realm.EPOCH_COUNTER = realm.EPOCH_COUNTER + 1

        if steps:
            if realm.EPOCH_COUNTER > steps:
                return


if __name__ == "__main__":
    restore_from_s3()
    main_loop()
# dummy change
