from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.base_object import BaseObject


def find_nearest(obj, type_in, rad: int = 10):

    if isinstance(type_in, list):
        type_in = [obj_fut(t) for t in type_in]
    else:
        type_in = obj_fut(type_in)

    min_obj = None
    min_dist = -1
    min_i = -1
    min_j = -1

    for i in range(max(0, obj.x - rad), min(obj.x + rad, realm.MAP.size_x)):
        for j in range(max(0, obj.y - rad), min(obj.y + rad, realm.MAP.size_x)):
            obj_index_found = realm.TILES[(i, j)].occupied_by
            if obj_index_found:
                if type_in:

                    if isinstance(type_in, list):
                        obj_in_type = any(
                            [
                                isinstance(realm.OBJECT_LIST[obj_index_found], t)
                                for t in type_in
                            ]
                        )
                    else:
                        obj_in_type = isinstance(
                            realm.OBJECT_LIST[obj_index_found], type_in
                        )

                    if obj_in_type:
                        if (
                            min_dist > abs(obj.x - i) + abs(obj.y - j)
                        ) or min_dist == -1:
                            min_dist = abs(obj.x - i) + abs(obj.y - j)

                            min_i = i
                            min_j = j
                            min_obj = realm.OBJECT_LIST[obj_index_found]
                else:

                    if (min_dist > abs(obj.x - i) + abs(obj.y - j)) or min_dist == -1:
                        min_dist = abs(obj.x - i) + abs(obj.y - j)

                        min_i = i
                        min_j = j
                        min_obj = realm.OBJECT_LIST[obj_index_found]

    return min_obj


def find_objects_location(x: int, y: int, rad: int = 30):

    objects_found = {}

    for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
        for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_x)):
            obj_index_found = realm.TILES[(i, j)].occupied_by

            if obj_index_found:

                objects_found[obj_index_found] = realm.OBJECT_LIST[obj_index_found]

    return objects_found


def find_objects(obj: BaseObject, rad: int = 30):

    return find_objects_location(obj.x, obj.y, rad=rad)


def find_tiles_location(x: int, y: int, rad: int = 30):

    tiles = {}

    for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
        for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_x)):
            tiles[(i, j)] = realm.TILES[(i, j)]

    return tiles


def find_tiles(obj: BaseObject, rad: int = 30):

    obj = obj_fut(obj)

    return find_tiles_location(obj.x, obj.y, rad)


def find_particles_location(x: int, y: int, rad: int = 30):

    particles_found = {}

    for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
        for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_x)):

            particles_index_found = realm.TILES[(i, j)].occupied_by_particles

            if particles_index_found:
                for particle_index_found in particles_index_found:

                    particles_found[particle_index_found] = realm.PARTICLE_LIST[
                        particle_index_found
                    ]

    return particles_found


def find_particles(obj, rad: int = 30):

    return find_particles_location(obj.x, obj.y, rad)


def get_nearest_free_location(x, y):

    rad = 1

    while rad < realm.MAP.size_x:

        for i in [max(0, x - rad), min(x + rad, realm.MAP.size_x)]:
            for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_y)):
                tile = realm.TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
            for j in [max(0, y - rad), min(y + rad, realm.MAP.size_y)]:
                tile = realm.TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        rad = rad + 1

    return None
