global chasing_num, random_num, run_away_num, chasing_dir, run_away_dir, mode, last_x, last_y, stuck_num

if not chasing_num:
    chasing_num = 0

if not random_num:
    random_num = 0

if not run_away_num:
    run_away_num = 0

if not chasing_dir:
    chasing_dir = 0

if not run_away_dir:
    run_away_dir = 0

if not mode:
    mode = 'random'

if not last_x:
    last_x = 0

if not last_y:
    last_y = 0

if not stuck_num:
    stuck_num = 0

intent = None

found_fox_obj = None

chase_from = ["Fox"]

if chase_from:
    if mode not in ["random", "run_away"]:

        found_fox_obj = find_nearest_xy(
            parent_object["x"], parent_object["y"], chase_from, rad=10
        )

        if found_fox_obj:
            mode = "run_away"

if mode == "run_away":
    if not found_fox_obj:
        found_fox_obj = find_nearest_xy(
            parent_object["x"], parent_object["y"], chase_from, rad=10
        )

        if not found_fox_obj:
            mode = "chase"

    if run_away_num == 0:

        run_away_dir = random_randint(0, 2) > 0

    run_away_num = run_away_num + 1

    if (last_x == parent_object["x"]) and (last_y == parent_object["y"]):
        stuck_num = stuck_num + 1

    if (run_away_num > 50) or (stuck_num > 5):
        stuck_num = 0
        chasing_num = 0
        run_away_num = 0
        mode = "random"

    found_obj = found_fox_obj

    if found_obj:

        if chasing_dir:

            if found_obj["x"] > parent_object["x"]:
                if parent_object["rotation"] == "LEFT":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_LEFT"

            elif found_obj["x"] < parent_object["x"]:
                if parent_object["rotation"] == "RIGHT":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_RIGHT"

            elif found_obj["x"] == parent_object["x"]:
                run_away_dir = not (run_away_dir)

        if not chasing_dir:

            if found_obj["y"] > parent_object["y"]:
                if parent_object["rotation"] == "UP":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_UP"

            elif found_obj["y"] < parent_object["y"]:
                if parent_object["rotation"] == "DOWN":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_DOWN"

            elif found_obj["y"] == parent_object["y"]:
                run_away_dir = not (run_away_dir)

if mode == "chase":

    if chasing_num == 0:

        chasing_dir = random_randint(0, 1) > 0

    chasing_num = chasing_num + 1

    if (last_x == parent_object["x"]) and (last_y == parent_object["y"]):
        stuck_num = stuck_num + 1

    if (chasing_num > 50) or (stuck_num > 5):
        stuck_num = 0
        chasing_num = 0
        run_away_num = 0
        mode = "random"

    chase_after = ["Grass", "Grass2", "Grass3", "Seed", "Seed2", "Seed3"]

    found_obj = find_nearest_xy(
        parent_object["x"], parent_object["y"], chase_after, rad=10
    )

    if found_obj:

        if chasing_dir:

            if found_obj["x"] > parent_object["x"]:
                if parent_object["rotation"] == "RIGHT":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_RIGHT"

            elif found_obj["x"] < parent_object["x"]:
                if parent_object["rotation"] == "LEFT":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_LEFT"

            elif found_obj["x"] == parent_object["x"]:
                chasing_dir = not (chasing_dir)

        if not chasing_dir:

            if found_obj["y"] > parent_object["y"]:
                if parent_object["rotation"] == "DOWN":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_DOWN"

            elif found_obj["y"] < parent_object["y"]:
                if parent_object["rotation"] == "UP":
                    intent = "MOVE_FORWARD"
                else:
                    intent = "ROTATE_UP"

            elif found_obj["y"] == parent_object["y"]:
                chasing_dir = not (chasing_dir)

    else:

        if random_randint(0, 5) >= 4:
            intent = random_choice(
                [
                    "ROTATE_UP",
                    "ROTATE_RIGHT",
                    "ROTATE_DOWN",
                    "ROTATE_LEFT",
                    "MOVE_FORWARD",
                ]
            )
        else:
            intent = "MOVE_FORWARD"

if mode == "random":

    if (last_x == parent_object["x"]) and (last_y == parent_object["y"]):
        stuck_num = stuck_num + 1

    if random_num > 5:
        random_num = 0
        stuck_num = 0
        mode = "chase"

    random_num = random_num + 1

    if (stuck_num % 2) == 0:
        intent = ["ROTATE_UP", "ROTATE_RIGHT", "ROTATE_DOWN", "ROTATE_LEFT"][(stuck_num//2)%4]
    else:
        intent = "MOVE_FORWARD"

last_x = parent_object["x"]
last_y = parent_object["y"]
