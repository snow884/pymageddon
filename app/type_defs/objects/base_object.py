from dataclasses import dataclass

from common_utils.common_enums import Actions, Rotations
from dataclasses_json import dataclass_json
from sandboxed_language.evaluator import evaluate_code
from singleton import realm
from type_defs.particles.score20_effect import Score20Particle
from type_defs.particles.score100_effect import Score100Particle
from type_defs.particles.score200_effect import Score200Particle
from type_defs.particles.score500_effect import Score500Particle
from type_defs.particles.score1000_effect import Score1000Particle
from type_defs.utils.utils import Spectator


@dataclass_json
@dataclass
class BaseObject:

    index: int = 0
    type_name: str = "Undefined"
    hp: int = 50
    is_alive: bool = False

    is_player: bool = False

    is_particle: bool = False

    player_name: str = ""

    family_name: str = "default"

    image: str = ""
    intent: Actions = None

    score: int = 0

    x: int = 0
    y: int = 0

    rgb_map: object = (0, 0, 0)

    rotation: int = Rotations.UP

    variables: object = None

    effects: object = None

    code: str = ""
    code_store: str = ""

    died_flag: bool = False

    def __init__(
        self,
        x_new: int,
        y_new: int,
        is_player=False,
        player_name=None,
        code=None,
        code_store=None,
        family_name=None,
    ):

        super().__init__()

        self.variables = {}

        self.index = realm.OBJ_COUNTER
        realm.OBJ_COUNTER = realm.OBJ_COUNTER + 1

        if realm.TILES[(x_new, y_new)].occupied_by is not None:
            raise Exception(
                f"The position [{x_new},{y_new}] is already occupied by"
                f" {realm.OBJECT_LIST[realm.TILES[(x_new,y_new)].occupied_by]}"
            )

        realm.OBJECT_LIST[self.index] = self
        realm.TILES[(x_new, y_new)].occupied_by = self.index

        if is_player:
            self.player_name = player_name
            realm.PLAYER_LIST[self.player_name] = self

        self.x = x_new
        self.y = y_new
        self.is_player = is_player
        self.code = code
        self.code_store = code_store
        self.family_name = family_name

    def __str__(self) -> str:

        return self.type_name + f" (ID {self.index})"

    def get_description_short(self) -> str:

        return ""

    def get_description_long(self) -> str:

        if self.effects:

            effects_str = "".join(eff.description() for eff in self.effects)
        else:
            effects_str = ""

        return self.get_description_short() + "\n" + effects_str

    def move_to_position(self, x_new: int, y_new: int) -> bool:

        if x_new >= realm.MAP.size_x or x_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the realm.MAP size {realm.MAP.size_x }x{realm.MAP.size_y}")
            return False

        if y_new >= realm.MAP.size_y or y_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the realm.MAP size {realm.MAP.size_x }x{realm.MAP.size_y}")
            return False

        if realm.TILES[(x_new, y_new)].occupied_by is not None:
            # print(f"The position [{x_new},{y_new}] is already occupied by {realm.OBJECT_LIST[realm.TILES[(x_new,y_new)].occupied_by]}")
            return False

        realm.TILES[(self.x, self.y)].occupied_by = None
        realm.TILES[(x_new, y_new)].occupied_by = self.index

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
        if self.code:
            intent, user_variables, error = evaluate_code(
                code_in=self.code, user_variables=self.variables, parent_object=self
            )

            if error:
                self.variables = {"error": error}
                return None

            self.variables = user_variables

            return intent

    def run_effects(self):

        if self.is_alive:
            self.score += 1

            if self.score == 20:
                Score20Particle(x_new=self.x, y_new=self.y)

            if self.score == 100:
                Score100Particle(x_new=self.x, y_new=self.y)

            if self.score == 200:
                Score200Particle(x_new=self.x, y_new=self.y)

            if self.score == 500:
                Score500Particle(x_new=self.x, y_new=self.y)

            if self.score == 1000:
                Score1000Particle(x_new=self.x, y_new=self.y)

        for e in self.effects:
            e.run_effect(self)

    def update_score(self):

        if self.is_player:
            score_dict = realm.SCORE_LIST["players"].get(
                self.player_name,
                {
                    "player_score": 0,
                    "player_score_rank": 0,
                    "family_score": 0,
                    "family_score_rank": 0,
                    "player_games": 0,
                    "player_games_rank": 0,
                    "family_games": 0,
                    "family_games_rank": 0,
                },
            )

            if score_dict["player_score"] < self.score or (not self.score):

                score_dict["player_score"] = self.score

            score_dict["player_games"] += 1

            realm.SCORE_LIST["players"][self.player_name] = score_dict

        else:
            if self.family_name:
                score_dict = realm.SCORE_LIST["players"].get(
                    self.family_name,
                    {
                        "player_score": 0,
                        "family_score": 0,
                        "player_games": 0,
                        "family_games": 0,
                    },
                )

                score_dict["family_score"] += self.score

                score_dict["family_games"] += 1

                realm.SCORE_LIST["players"][self.family_name] = score_dict

        for score_type in [
            "player_score",
            "family_score",
            "player_games",
            "family_games",
        ]:

            my_dict = {p: d[score_type] for p, d in realm.SCORE_LIST["players"].items()}

            sorted_items = sorted(
                my_dict.items(), key=lambda item: item[1], reverse=True
            )

            for rank, (key, value) in enumerate(sorted_items, 1):
                realm.SCORE_LIST["ranking"][rank] = key
                realm.SCORE_LIST["players"][key][score_type + "_rank"] = rank

    def die(self, player_afterlife=True):

        if self.died_flag:
            return

        self.died_flag = True

        self.update_score()

        realm.TILES[(self.x, self.y)].occupied_by = None

        del realm.OBJECT_LIST[self.index]

        if self.index in realm.SPECTATOR_LIST:

            Spectator(
                obj=realm.TILES[(self.x, self.y)],
                player_name=realm.SPECTATOR_LIST[self.index].player_name,
                object_type="tile",
                lifetime=10,
                large_message="The bot has been killed !",
            )

            del realm.SPECTATOR_LIST[self.index]

        if self.is_player:
            if player_afterlife:
                Spectator(
                    obj=realm.TILES[(self.x, self.y)],
                    player_name=self.player_name,
                    object_type="tile",
                    lifetime=10,
                    large_message="You have been killed !",
                )

            print(f"Player {self.player_name} died")
            del realm.PLAYER_LIST[self.player_name]
