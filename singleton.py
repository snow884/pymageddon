class Realm:
    TILES = {}
    OBJECT_LIST = {}
    PLAYER_LIST = {}
    PARTICLE_LIST = {}
    OBJ_COUNTER = 0
    MAP_VIEW_SIZE = 11
    TIME_INTERVAL = 0.66
    EPOCH_COUNTER = 0
    MAP = None

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.TILES = {}
        self.OBJECT_LIST = {}
        self.PLAYER_LIST = {}
        self.PARTICLE_LIST = {}
        self.OBJ_COUNTER = 0
        self.MAP_VIEW_SIZE = 11
        self.TIME_INTERVAL = 0.66
        self.EPOCH_COUNTER = 0
        self.MAP = None
        self.REDIS_CONNECTION = None


realm = Realm()
