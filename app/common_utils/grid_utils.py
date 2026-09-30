from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.base_object import BaseObject


def find_nearest(obj, type_in, rad: int = 10):

    if isinstance(type_in, (list, tuple)):
        type_tuple = tuple(obj_fut(t) for t in type_in)
    else:
        type_tuple = obj_fut(type_in)

    rad_check = 0

    while rad_check < rad:
        rad_check += 1

        for i in [
            max(0, obj.x - rad_check),
            min(obj.x + rad_check, realm.MAP.size_x - 1),
        ]:
            for j in range(
                max(0, obj.y - rad_check), min(obj.y + rad_check, realm.MAP.size_y)
            ):
                tile = realm.TILES[(i, j)]
                if tile.occupied_by is not None:
                    target_obj = realm.OBJECT_LIST.get(tile.occupied_by)
                    if target_obj is not None and isinstance(target_obj, type_tuple):
                        return target_obj

        for i in range(
            max(0, obj.x - rad_check), min(obj.x + rad_check, realm.MAP.size_x)
        ):
            for j in [
                max(0, obj.y - rad_check),
                min(obj.y + rad_check, realm.MAP.size_y - 1),
            ]:
                tile = realm.TILES[(i, j)]
                if tile.occupied_by is not None:
                    target_obj = realm.OBJECT_LIST.get(tile.occupied_by)
                    if target_obj is not None and isinstance(target_obj, type_tuple):
                        return target_obj

    return None


def find_objects_location(x: int, y: int, rad: int = 30):

    objects_found = {}

    for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
        for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_x)):
            obj_index_found = realm.TILES[(i, j)].occupied_by

            if obj_index_found is not None:

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

        for i in [max(0, x - rad), min(x + rad, realm.MAP.size_x - 1)]:
            for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_y)):
                tile = realm.TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
            for j in [max(0, y - rad), min(y + rad, realm.MAP.size_y - 1)]:
                tile = realm.TILES[(i, j)]
                if not tile.occupied_by:
                    return i, j

        rad = rad + 1

    return None
