if random_randint(0, 5) >= 4:
    intent = random_choice(
        ["ROTATE_UP", "ROTATE_RIGHT", "ROTATE_DOWN", "ROTATE_LEFT", "MOVE_FORWARD"]
    )
else:
    intent = "MOVE_FORWARD"
