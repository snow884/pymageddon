from common_utils.utils import obj_fut
from singleton import realm


def set_index(list_in, index, val):

    list_in[index] = val


def get_index(list_in, index):

    return list_in[index]


def find_nearest_xy(x, y, type_in, rad: int = 10):

    if isinstance(type_in, list):
        type_in = [obj_fut(t) for t in type_in]
    else:
        type_in = obj_fut(type_in)

    min_obj = None
    min_dist = -1
    min_i = -1
    min_j = -1

    for i in range(max(0, x - rad), min(x + rad, realm.MAP.size_x)):
        for j in range(max(0, y - rad), min(y + rad, realm.MAP.size_x)):
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
                        if (min_dist > abs(x - i) + abs(y - j)) or min_dist == -1:
                            min_dist = abs(x - i) + abs(y - j)

                            min_i = i
                            min_j = j
                            min_obj = realm.OBJECT_LIST[obj_index_found]
                else:

                    if (min_dist > abs(x - i) + abs(y - j)) or min_dist == -1:
                        min_dist = abs(x - i) + abs(y - j)

                        min_i = i
                        min_j = j
                        min_obj = realm.OBJECT_LIST[obj_index_found]

    return [min_obj.x, min_obj.y]
