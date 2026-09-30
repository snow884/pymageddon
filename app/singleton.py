import threading


class Realm:
    MODE = "full"
    TILES = {}
    OBJECT_LIST = {}
    PLAYER_LIST = {}
    SPECTATOR_LIST = {}
    PARTICLE_LIST = {}
    OBJ_COUNTER = 0
    MAP_VIEW_SIZE = 12
    TIME_INTERVAL = 0.33
    LAST_REFRESH_TIME = 0.33
    EPOCH_COUNTER = 0
    MAP = None
    SCORE_LIST = None
    REDIS_CONNECTION = None

    # Guards concurrent access to the shared game state (TILES, OBJECT_LIST,
    # PLAYER_LIST, SPECTATOR_LIST, PARTICLE_LIST) which is mutated by the main
    # game loop thread while being read by the background worker threads
    # (map sending, plot/summary generation). Without this lock, dicts can be
    # mutated while another thread iterates over them, raising intermittent
    # "dictionary changed size during iteration" errors that get silently
    # swallowed and cause the game to appear glitchy or to stall.
    LOCK = threading.RLock()

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
        self.TIME_INTERVAL = 0.33
        self.LAST_REFRESH_TIME = 0.33
        self.EPOCH_COUNTER = 0
        self.MAP = None
        self.SCORE_LIST = None
        self.REDIS_CONNECTION = None
        self.LOCK = threading.RLock()


realm = Realm()
