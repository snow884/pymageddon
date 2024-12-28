import random

from common_utils.common_enums import Actions, Rotations
from common_utils.grid_utils import find_nearest


def simple_chase(parent_object, chase_after=[], chase_from=[]):

    chasing_num = parent_object.variables.get("chasing_num", 0)
    random_num = parent_object.variables.get("random_num", 0)
    run_away_num = parent_object.variables.get("run_away_num", 0)

    chasing_dir = parent_object.variables.get("chasing_dir", False)
    run_away_dir = parent_object.variables.get("run_away_dir", 0)

    mode = parent_object.variables.get("mode", "chase")

    last_x = parent_object.variables.get("last_x", 0)
    last_y = parent_object.variables.get("last_y", 0)

    stuck_num = parent_object.variables.get("stuck_num", 0)

    intent = None

    found_fox_obj = None

    if chase_from:
        if mode not in ["random", "run_away"]:

            found_fox_obj = find_nearest(parent_object, chase_from)

            if found_fox_obj:
                mode = "run_away"

    if mode == "run_away":
        if not found_fox_obj:
            found_fox_obj = find_nearest(parent_object, chase_from)

        if run_away_num == 0:

            run_away_dir = random.randint(0, 2) > 0

        run_away_num = run_away_num + 1

        if (last_x == parent_object.x) or (last_y == parent_object.y):
            stuck_num = stuck_num + 1

        if (run_away_num > 50) or (stuck_num > 2):
            stuck_num = 0
            chasing_num = 0
            mode = "random"

        found_obj = found_fox_obj

        if found_obj:

            if chasing_dir:

                if found_obj.x > parent_object.x:
                    if parent_object.rotation == Rotations.LEFT:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_LEFT

                if found_obj.x < parent_object.x:
                    if parent_object.rotation == Rotations.RIGHT:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_RIGHT

                if found_obj.x == parent_object.x:
                    run_away_dir = not (run_away_dir)

            else:

                if found_obj.y > parent_object.y:
                    if parent_object.rotation == Rotations.UP:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_UP

                if found_obj.y < parent_object.y:
                    if parent_object.rotation == Rotations.DOWN:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_DOWN

                if found_obj.y == parent_object.y:
                    run_away_dir = not (run_away_dir)

    if mode == "chase":

        if chasing_num == 0:

            chasing_dir = random.randint(0, 2) > 0

        chasing_num = chasing_num + 1

        if (last_x == parent_object.x) or (last_y == parent_object.y):
            stuck_num = stuck_num + 1

        if (chasing_num > 50) or (stuck_num > 2):
            stuck_num = 0
            chasing_num = 0
            mode = "random"

        found_obj = find_nearest(parent_object, chase_after)

        if found_obj:

            if chasing_dir:

                if found_obj.x > parent_object.x:
                    if parent_object.rotation == Rotations.RIGHT:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_RIGHT

                if found_obj.x < parent_object.x:
                    if parent_object.rotation == Rotations.LEFT:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_LEFT

                if found_obj.x == parent_object.x:
                    chasing_dir = not (chasing_dir)

            else:

                if found_obj.y > parent_object.y:
                    if parent_object.rotation == Rotations.DOWN:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_DOWN

                if found_obj.y < parent_object.y:
                    if parent_object.rotation == Rotations.UP:
                        intent = Actions.MOVE_FORWARD
                    else:
                        intent = Actions.ROTATE_UP

                if found_obj.y == parent_object.y:
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

    last_x = parent_object.x
    last_y = parent_object.y

    parent_object.variables["last_x"] = last_x
    parent_object.variables["last_y"] = last_y

    parent_object.variables["stuck_num"] = stuck_num

    parent_object.variables["chasing_num"] = chasing_num
    parent_object.variables["random_num"] = random_num
    parent_object.variables["run_away_num"] = run_away_num

    parent_object.variables["chasing_dir"] = chasing_dir
    parent_object.variables["run_away_dir"] = run_away_dir

    parent_object.variables["mode"] = mode

    return intent
