import json
import random
import time
from dataclasses import dataclass
from enum import Enum

import redis
from dataclasses_json import dataclass_json

r = redis.Redis(host="localhost", port=6379, db=0)

# Custom JSON encoder
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


class Rotations(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Actions(Enum):

    ROTATE_UP = 1
    ROTATE_RIGHT = 2
    ROTATE_DOWN = 3
    ROTATE_LEFT = 4

    MOVE_FORWARD = 6


@dataclass
class Map:

    size_x: int = 0
    size_y: int = 0


@dataclass_json
@dataclass
class Tile:

    index: int = 0
    type_name: str = "Undefined"
    x: int = 0
    y: int = 0
    rotation: int = Rotations.UP
    image: str = ""
    occupied_by: int = None
    occupied_by_particles = None

    def __init__(self, x, y):

        super().__init__()

        self.x = x
        self.y = y

        self.occupied_by_particles = []


@dataclass_json
@dataclass
class Player:
    name = ""


@dataclass_json
@dataclass
class Particle:
    x: int = 0
    y: int = 0

    index: int = 0

    type_name: str = "Undefined"

    image: str = ""

    lifetime: int = 3
    life: int = 0

    def __init__(self, x_new: int, y_new: int):

        super().__init__()

        global OBJ_COUNTER, OBJECT_LIST, TILES, PARTICLE_LIST

        self.index = OBJ_COUNTER
        OBJ_COUNTER = OBJ_COUNTER + 1

        PARTICLE_LIST[self.index] = self
        TILES[(x_new, y_new)].occupied_by_particles.append(self.index)

        self.x = x_new
        self.y = y_new

    def effects(self):
        self.life = self.life + 1
        if self.life >= self.lifetime:
            self.die()

    def die(self):
        TILES[(self.x, self.y)].occupied_by_particles = list(
            set(TILES[(self.x, self.y)].occupied_by_particles) - set([self.index])
        )
        del PARTICLE_LIST[self.index]


class DeathParticle(Particle):

    type_name: str = "Death"

    image: str = "static/particles/skull.png"

    lifetime: int = 3


@dataclass_json
@dataclass
class MyObject:

    index: int = 0
    type_name: str = "Undefined"
    hp: int = 50
    is_alive: bool = False

    is_player: bool = False
    player_name: str = ""

    image: str = ""
    intent: Actions = None

    x: int = 0
    y: int = 0
    rotation: int = Rotations.UP

    variables: object = None

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):

        super().__init__()

        self.variables = {}

        global OBJ_COUNTER, OBJECT_LIST, TILES

        self.index = OBJ_COUNTER
        OBJ_COUNTER = OBJ_COUNTER + 1

        if TILES[(x_new, y_new)].occupied_by is not None:
            raise Exception(
                f"The position [{x_new},{y_new}] is already occupied by"
                f" {OBJECT_LIST[TILES[(x_new,y_new)].occupied_by]}"
            )

        OBJECT_LIST[self.index] = self
        TILES[(x_new, y_new)].occupied_by = self.index

        if is_player:
            self.player_name = player_name
            PLAYER_LIST[self.player_name] = self

        self.x = x_new
        self.y = y_new
        self.is_player = is_player

    def __str__(self) -> str:

        return self.type_name + f" (ID {self.index})"

    def move_to_position(self, x_new: int, y_new: int) -> bool:

        if x_new >= MAP.size_x or x_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the map size {MAP.size_x }x{MAP.size_y}")
            return False

        if y_new >= MAP.size_y or y_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the map size {MAP.size_x }x{MAP.size_y}")
            return False

        if TILES[(x_new, y_new)].occupied_by is not None:
            # print(f"The position [{x_new},{y_new}] is already occupied by {OBJECT_LIST[TILES[(x_new,y_new)].occupied_by]}")
            return False

        TILES[(self.x, self.y)].occupied_by = None
        TILES[(x_new, y_new)].occupied_by = self.index

        self.x = x_new
        self.y = y_new

        return True

    def get_next_coords(self, direction=1):

        if not self.intent == Actions.MOVE_FORWARD:
            return self.x, self.y
        else:

            x_new = self.x
            y_new = self.y

            if self.rotation == Rotations.UP:

                y_new = self.y - 1 * direction

            elif self.rotation == Rotations.RIGHT:

                x_new = self.x + 1 * direction

            elif self.rotation == Rotations.DOWN:

                y_new = self.y + 1 * direction

            elif self.rotation == Rotations.LEFT:

                x_new = self.x - 1 * direction

            return x_new, y_new

    def think(self):
        pass

    def effects(self):
        pass

    def die(self):
        TILES[(self.x, self.y)].occupied_by = None
        del OBJECT_LIST[self.index]

        if self.is_player:
            del PLAYER_LIST[self.player_name]

    def chase_objects(self, obj_types, dir):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, obj_types)

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent


def find_nearest(obj: MyObject, type_in, rad: int = 10):

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


def find_objects(obj: MyObject, rad: int = 30):

    objects_found = {}

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):
            obj_index_found = TILES[(i, j)].occupied_by

            if obj_index_found:

                objects_found[obj_index_found] = OBJECT_LIST[obj_index_found]

    return objects_found


def find_tiles(obj: MyObject, rad: int = 30):

    tiles = {}

    for i in range(max(0, obj.x - rad), min(obj.x + rad, MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, MAP.size_x)):
            tiles[(i, j)] = TILES[(i, j)]

    return tiles


def find_particles(obj: MyObject, rad: int = 30):

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


class Tile1(Tile):

    type_name: str = "Tile1"

    image: str = "static/tiles/tile1.png"


class Grass(MyObject):

    type_name: str = "Grass"

    image = "static/objects/grass.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1

        if life_length > 10:

            x_new = random.choice([-1, 0, 1]) + self.x
            y_new = random.choice([-1, 0, 1]) + self.y

            tile = TILES.get((x_new, y_new))

            if tile:
                if tile.occupied_by is None:
                    obj_fut("Seed")(x_new=x_new, y_new=y_new)

            life_length = 0

        self.variables["life_length"] = life_length


class Seed(MyObject):
    type_name: str = "Seed"
    image = "static/objects/seed.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:
            x_new = self.x
            y_new = self.y

            self.die()
            Grass(x_new=x_new, y_new=y_new)


class ChickenEgg(MyObject):
    type_name: str = "ChickenEgg"
    image = "static/objects/egg.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:
            x_new = self.x
            y_new = self.y

            self.die()
            Chicken(x_new=x_new, y_new=y_new)


class CowEgg(MyObject):
    type_name: str = "CowEgg"
    image = "static/objects/egg.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:
            x_new = self.x
            y_new = self.y

            self.die()
            Cow(x_new=x_new, y_new=y_new)


class FoxEgg(MyObject):
    type_name: str = "FoxEgg"
    image = "static/objects/egg.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:
            x_new = self.x
            y_new = self.y

            self.die()
            Fox(x_new=x_new, y_new=y_new)


class Stone(MyObject):
    type_name: str = "Stone"
    image = "static/objects/stone.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )


class Angel(MyObject):

    type_name: str = "Angel"
    image = "static/objects/angel.png"
    is_alive = True

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):
        super().__init__(
            x_new=x_new, y_new=y_new, is_player=is_player, player_name=player_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, [Fox, Cow, Chicken])

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent

    def effects(self):

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 50:

            x_new, y_new = self.get_next_coords(-1)
            tile = TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:
                    if random.randint(0, 4) == 3:
                        random.choice([ChickenEgg, CowEgg, FoxEgg])(
                            x_new=x_new, y_new=y_new
                        )
                    else:
                        Seed(x_new=x_new, y_new=y_new)
                    life_length = 0
                    self.variables["life_length"] = life_length


class Chicken(MyObject):

    type_name: str = "Chicken"
    image = "static/objects/chicken.png"
    is_alive = True

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):
        super().__init__(
            x_new=x_new, y_new=y_new, is_player=is_player, player_name=player_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, [Seed])

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent

    def effects(self):

        if self.intent == Actions.MOVE_FORWARD:
            x_new, y_new = self.get_next_coords()

            tile = TILES.get((x_new, y_new))

            if tile:

                occupied_by_obj_index = tile.occupied_by
                if occupied_by_obj_index:
                    obj_on_location = OBJECT_LIST[occupied_by_obj_index]
                    if isinstance(obj_on_location, Seed):

                        obj_on_location.die()
                        self.hp = min(self.hp + 50, 100)

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:

            x_new, y_new = self.get_next_coords(-1)
            tile = TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:
                    ChickenEgg(x_new=x_new, y_new=y_new)
                    life_length = 0
                    self.variables["life_length"] = life_length

        self.hp = self.hp - 1

        if self.hp <= 0:
            self.die()

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()


class Cow(MyObject):

    type_name: str = "Cow"
    image = "static/objects/cow.png"
    is_alive = True

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):
        super().__init__(
            x_new=x_new, y_new=y_new, is_player=is_player, player_name=player_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, [Seed, Grass])

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent

    def effects(self):

        if self.intent == Actions.MOVE_FORWARD:
            x_new, y_new = self.get_next_coords()

            tile = TILES.get((x_new, y_new))

            if tile:

                occupied_by_obj_index = tile.occupied_by
                if occupied_by_obj_index:
                    obj_on_location = OBJECT_LIST[occupied_by_obj_index]
                    if isinstance(obj_on_location, Seed) or isinstance(
                        obj_on_location, Grass
                    ):

                        obj_on_location.die()

                        self.hp = min(self.hp + 50, 100)

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:

            x_new, y_new = self.get_next_coords(-1)
            tile = TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:
                    CowEgg(x_new=x_new, y_new=y_new)
                    life_length = 0
                    self.variables["life_length"] = life_length

        self.hp = self.hp - 1

        if self.hp <= 0:
            self.die()

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()


class Fox(MyObject):

    type_name: str = "Fox"

    image = "static/objects/fox.png"
    is_alive = True

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):
        super().__init__(
            x_new=x_new, y_new=y_new, is_player=is_player, player_name=player_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, [Cow, Chicken])

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent

    def effects(self):

        if self.intent == Actions.MOVE_FORWARD:
            x_new, y_new = self.get_next_coords()

            tile = TILES.get((x_new, y_new))

            if tile:

                occupied_by_obj_index = tile.occupied_by
                if occupied_by_obj_index:
                    obj_on_location = OBJECT_LIST[occupied_by_obj_index]
                    if (
                        isinstance(obj_on_location, Cow)
                        or isinstance(obj_on_location, Chicken)
                        or isinstance(obj_on_location, ChickenEgg)
                        or isinstance(obj_on_location, Fox)
                    ):

                        obj_on_location.die()

                        self.hp = min(self.hp + 50, 100)

        life_length = self.variables.get("life_length", 0)
        life_length = life_length + 1
        self.variables["life_length"] = life_length

        if life_length > 100:

            x_new, y_new = self.get_next_coords(-1)
            tile = TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:
                    FoxEgg(x_new=x_new, y_new=y_new)
                    life_length = 0
                    self.variables["life_length"] = life_length

        self.hp = self.hp - 1

        if self.hp <= 0:
            self.die()

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()


def obj_fut(str):

    found = [
        inheritor
        for inheritor in MyObject.__subclasses__()
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

    for key in r.keys():
        key_str = key.decode()

        if key_str.startswith("player_"):
            player_name = key_str.replace("player_", "")

            if player_name not in PLAYER_LIST.keys():

                x_new, y_new = get_nearest_free_location(10, 10)

                Cow(x_new=x_new, y_new=y_new, is_player=True, player_name=player_name)


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
