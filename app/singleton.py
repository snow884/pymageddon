class Realm:
    MODE = "full"
    TILES = {}
    OBJECT_LIST = {}
    PLAYER_LIST = {}
    PARTICLE_LIST = {}
    OBJ_COUNTER = 0
    MAP_VIEW_SIZE = 11
    TIME_INTERVAL = 0.66
    LAST_REFRESH_TIME = 0.66
    EPOCH_COUNTER = 0
    MAP = None
    SCORE_LIST = None
    REDIS_CONNECTION = None

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.TILES = {}
        self.OBJECT_LIST = {}
        self.SPECTATOR_LIST = {}
        self.PLAYER_LIST = {}
        self.PARTICLE_LIST = {}
        self.OBJ_COUNTER = 0
        self.MAP_VIEW_SIZE = 12
        self.TIME_INTERVAL = 1.0
        self.EPOCH_COUNTER = 0
        self.MAP = None
        self.SCORE_LIST = None
        self.REDIS_CONNECTION = None


realm = Realm()
