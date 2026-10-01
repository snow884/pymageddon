from common_utils.common_enums import Actions, Rotations
from sandboxed_language.evaluator import eval_math, evaluate_code
from sandboxed_language.utils import find_nearest_xy, get_index, set_index
from type_defs.objects.cow import Cow
from type_defs.objects.grass import Grass


class TestSandboxedUtils:
    def test_get_and_set_index(self):
        data = {"a": 10, "b": 20}
        assert get_index(data, "a") == 10
        set_index(data, "a", 30)
        assert get_index(data, "a") == 30

        lst = [1, 2, 3]
        assert get_index(lst, 1) == 2
        set_index(lst, 1, 99)
        assert lst[1] == 99

    def test_find_nearest_xy(self, setup_small_grid):
        setup_small_grid(10, 10)
        Grass(x_new=5, y_new=5)
        Grass(x_new=2, y_new=2)

        nearest = find_nearest_xy(x=1, y=1, type_in="Grass", rad=5)
        assert nearest is not None
        assert nearest["x"] == 2
        assert nearest["y"] == 2

    def test_find_nearest_xy_none(self, setup_small_grid):
        setup_small_grid(10, 10)
        Grass(x_new=8, y_new=8)
        nearest = find_nearest_xy(x=0, y=0, type_in="Grass", rad=3)
        assert nearest is None


class TestEvalMath:
    def test_arithmetic_operators(self):
        assert eval_math("2 + 3") == 5
        assert eval_math("10 - 4") == 6
        assert eval_math("3 * 4") == 12
        assert eval_math("15 / 3") == 5.0
        assert eval_math("17 // 3") == 5
        assert eval_math("17 % 3") == 2
        assert eval_math("2 ** 3") == 8
        assert eval_math("-5") == -5

    def test_comparisons(self):
        assert eval_math("5 == 5") is True
        assert eval_math("5 != 4") is True
        assert eval_math("3 < 5") is True
        assert eval_math("5 <= 5") is True
        assert eval_math("7 > 2") is True
        assert eval_math("2 >= 2") is True
        assert eval_math("3 in [1, 2, 3]") is True
        assert eval_math("4 not in [1, 2, 3]") is True

    def test_boolean_logic(self):
        assert eval_math("True and False") is False
        assert eval_math("True or False") is True
        assert eval_math("not False") is True

    def test_complex_structures(self):
        assert eval_math("[1, 2, 3]") == [1, 2, 3]
        assert eval_math("(1, 2)") == (1, 2)
        assert eval_math("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}
        assert eval_math("{'a': 10}['a']") == 10
        assert eval_math("[10, 20, 30][1]") == 20


class TestEvaluateCode:
    def test_basic_variable_assignment(self):
        code = """
a = 10
b = 20
c = a + b
"""
        intent, user_vars, error = evaluate_code(code)
        assert error == ""
        assert intent is None
        assert user_vars["a"] == 10
        assert user_vars["b"] == 20
        assert user_vars["c"] == 30

    def test_intent_setting(self):
        code = """
intent = 'MOVE_FORWARD'
"""
        intent, user_vars, error = evaluate_code(code)
        assert error == ""
        assert intent == Actions.MOVE_FORWARD

    def test_rotations_intents(self):
        for act_str, expected in [
            ("ROTATE_UP", Actions.ROTATE_UP),
            ("ROTATE_RIGHT", Actions.ROTATE_RIGHT),
            ("ROTATE_DOWN", Actions.ROTATE_DOWN),
            ("ROTATE_LEFT", Actions.ROTATE_LEFT),
        ]:
            code = f"intent = '{act_str}'"
            intent, user_vars, error = evaluate_code(code)
            assert intent == expected

    def test_if_else_control_flow(self):
        code = """
x = 5
if x > 3:
    y = 100
    intent = 'ROTATE_UP'
else:
    y = 0
"""
        intent, user_vars, error = evaluate_code(code)
        assert user_vars["y"] == 100
        assert intent == Actions.ROTATE_UP

    def test_parent_object_access(self, setup_small_grid):
        setup_small_grid(10, 10)
        cow = Cow(x_new=3, y_new=4)
        cow.rotation = Rotations.RIGHT

        code = """
my_x = parent_object['x']
my_y = parent_object['y']
my_rot = parent_object['rotation']
if my_x == 3:
    intent = 'MOVE_FORWARD'
"""
        intent, user_vars, error = evaluate_code(code, parent_object=cow)
        assert error == ""
        assert user_vars["my_x"] == 3
        assert user_vars["my_y"] == 4
        assert user_vars["my_rot"] == "RIGHT"
        assert intent == Actions.MOVE_FORWARD

    def test_multi_turn_state_persistence(self):
        code = """
global counter
if not counter:
    counter = 1
else:
    counter = counter + 1
"""
        intent, vars1, _ = evaluate_code(code, user_variables={})
        assert vars1["counter"] == 1

        intent, vars2, _ = evaluate_code(code, user_variables=vars1)
        assert vars2["counter"] == 2

        intent, vars3, _ = evaluate_code(code, user_variables=vars2)
        assert vars3["counter"] == 3

    def test_syntax_error_handled(self):
        code = "this is not valid python !!!"
        intent, user_vars, error = evaluate_code(code)
        assert error != ""
        assert intent is None

    def test_find_nearest_xy_in_code(self, setup_small_grid):
        setup_small_grid(10, 10)
        Grass(x_new=5, y_new=3)
        code = """
target = find_nearest_xy(parent_object['x'], parent_object['y'], 'Grass', 10)
if target:
    found_x = target['x']
    found_y = target['y']
    intent = 'MOVE_FORWARD'
"""
        cow = Cow(x_new=1, y_new=1)
        intent, user_vars, error = evaluate_code(code, parent_object=cow)
        assert error == ""
        assert user_vars["found_x"] == 5
        assert user_vars["found_y"] == 3
        assert intent == Actions.MOVE_FORWARD


def _documented_bot_examples():
    import os
    import re

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs = ["README.md", os.path.join("app", "templates", "llms.txt")]
    examples = []
    for doc in docs:
        with open(os.path.join(root, doc)) as f:
            examples += re.findall(r"```python\n(.*?)```", f.read(), re.S)
    return examples


def test_documented_bot_example_runs(setup_small_grid):
    examples = _documented_bot_examples()
    assert len(examples) == 2
    setup_small_grid(10, 10)
    cow = Cow(x_new=1, y_new=1)
    Grass(x_new=5, y_new=1)

    for code in examples:
        cow.rotation = Rotations.UP
        intent, variables, error = evaluate_code(code, {}, parent_object=cow)
        assert error == ""
        assert intent == Actions.ROTATE_RIGHT

        cow.rotation = Rotations.RIGHT
        intent, variables, error = evaluate_code(code, variables, parent_object=cow)
        assert error == ""
        assert intent == Actions.MOVE_FORWARD
        assert variables["steps"] == 2
