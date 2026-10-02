import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Annotated, Optional

import jwt
import python_avatars as pa
import redis
from common_utils.utils import get_types_dict
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 31

SITE_URL = "https://pymageddon.ai-mmo-games.de"

app = FastAPI(
    title="Pymageddon API",
    version="1.0.0",
    description=(
        "Pymageddon is a free-to-play MMO survival game that simulates a living "
        "ecosystem with predator-prey dynamics. Players control a creature live "
        "or deploy a sandboxed Python bot to drive it. Obtain a bearer token "
        "from `POST /token` (set `is_guest: true` for an instant guest "
        f"account). Agent-oriented overview: {SITE_URL}/llms.txt"
    ),
)
r = redis.Redis(host="pymageddon-redis-server", port=6379, db=0)

origins = [
    "http://localhost:80",  # Your frontend's origin
    "http://localhost:80",  # Replace with your frontend's port if different
    "http://127.0.0.1:80",
    "http://0.0.0.0:80",
    "http://0.0.0.0:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)


@app.middleware("http")
async def no_cache_static_assets(request: Request, call_next):
    """Force browsers to revalidate /static assets on every load instead of
    serving them from the disk cache. StaticFiles still sends ETag/
    Last-Modified, so unchanged files get a cheap 304 while files replaced by
    a rebuild/deploy are always re-fetched instead of staying stuck on an
    old cached copy."""
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["site_url"] = SITE_URL


def time_ago(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{int(minutes)} minutes ago"
    hours = minutes // 60
    if hours < 24:
        return f"{int(hours)} hours ago"
    days = hours // 24
    if days < 30:
        return f"{int(days)} days ago"
    months = days // 30
    if months < 12:
        return f"{int(months)} months ago"

    years = months // 12
    return f"{int(years)} years ago"


class KeysPressed(BaseModel):
    ArrowRight: bool
    ArrowLeft: bool
    ArrowDown: bool
    ArrowUp: bool


class BotCode(BaseModel):
    code_str: str


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    verify_password: str


class BotCreate(BaseModel):
    request_type: str
    spectator_follow_type: str
    code: str


class NewGame(BaseModel):
    spectator_follow_index: Optional[int]
    spectator_follow_type: Optional[str]


class UserLogin(BaseModel):
    username: Optional[str] = ""
    password: Optional[str] = ""
    is_guest: Optional[bool] = False


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user_dict_str = r.get(f"player_{username}")
    if not user_dict_str:
        return None

    user_dict = json.loads(user_dict_str)

    return User(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: UserLogin,
) -> Token:

    if form_data.is_guest:

        username = "guest_" + str(uuid.uuid4().hex[0:8])
        password = "guest_" + str(uuid.uuid4().hex[0:8])

        res = create_player(
            UserCreate(username=username, password=password, verify_password=password)
        )

        if res["status"] == "success":
            user = authenticate_user(username, password)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cant create guest user",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/login_page", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(request=request, name="login.html", context={})


@app.get("/create_player_page", response_class=HTMLResponse)
def create_user_page(request: Request):

    return templates.TemplateResponse(
        request=request, name="create_user.html", context={}
    )


@app.get("/create_bot_page", response_class=HTMLResponse)
def create_bot_page(request: Request):

    return templates.TemplateResponse(
        request=request, name="create_bot_page.html", context={}
    )


@app.post("/new_game")
async def new_game(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_game_data: Optional[NewGame] = None,
):
    spectator_follow_index = None
    spectator_follow_type = None

    if new_game_data:
        spectator_follow_index = new_game_data.spectator_follow_index
        spectator_follow_type = new_game_data.spectator_follow_type

    if spectator_follow_index:
        r.set(
            f"game_{current_user.username}",
            json.dumps(
                {
                    "request_type": "spectator",
                    "spectator_follow_index": spectator_follow_index,
                    "spectator_follow_type": spectator_follow_type,
                }
            ),
        )
    else:
        r.set(
            f"game_{current_user.username}",
            json.dumps(
                {
                    "request_type": "player",
                    "spectator_follow_index": None,
                    "spectator_follow_type": None,
                }
            ),
        )

    return {"status": "success"}


@app.post("/end_game")
async def end_game(current_user: Annotated[User, Depends(get_current_active_user)]):

    r.set(
        f"game_{current_user.username}",
        json.dumps({"request_type": "end_game"}),
    )

    return {"status": "success"}


@app.get("/me")
async def end_game(current_user: Annotated[User, Depends(get_current_active_user)]):

    return {"user_name": current_user.username}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/explorer", response_class=HTMLResponse)
async def explorer(request: Request):

    all_objects_summary = json.loads(r.get(f"all_objects_summary"))

    return templates.TemplateResponse(
        request=request,
        name="explorer.html",
        context={"objects_summary": all_objects_summary},
    )


@app.get("/explorer/type/{type_name}/", response_class=HTMLResponse)
async def explorer_type(request: Request, type_name: str):

    all_objects_summary = json.loads(r.get(f"all_objects_summary"))

    type_summary = all_objects_summary[type_name]

    print(type_summary["effects"])

    return templates.TemplateResponse(
        request=request,
        name="explorer_type.html",
        context={"type_summary": type_summary},
    )


@app.get("/explorer", response_class=HTMLResponse)
async def explorer(request: Request):

    all_objects_summary = json.loads(r.get(f"all_objects_summary"))

    return templates.TemplateResponse(
        request=request,
        name="explorer.html",
        context={"objects_summary": all_objects_summary},
    )


@app.get("/players", response_class=HTMLResponse)
async def players(request: Request):

    all_players = {}

    curr_timestamp = time.time()

    for key in r.keys(pattern="player_*"):
        key_str = key.decode()

        player_name = key_str.replace("player_", "")

        score_str = r.get(f"score_{player_name}")

        if score_str:

            all_players[player_name] = json.loads(score_str)

    for player_name, _ in all_players.items():
        all_players[player_name]["player_scores"][
            "last_game_ago"
        ] = curr_timestamp - all_players[player_name]["player_scores"].get(
            "last_game", curr_timestamp
        )
        all_players[player_name]["player_scores"]["last_game_ago_str"] = time_ago(
            curr_timestamp
            - all_players[player_name]["player_scores"].get("last_game", curr_timestamp)
        )

    return templates.TemplateResponse(
        request=request,
        name="players.html",
        context={"all_players": all_players},
    )


@app.get("/players/{player_name}", response_class=HTMLResponse)
async def player(request: Request, player_name: str):

    curr_timestamp = time.time()

    score_str = r.get(f"score_{player_name}")

    score_summary = {}

    if score_str:

        score_summary = json.loads(score_str)

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    score_summary["player_name"] = player_name

    print(score_summary["player_scores"])

    score_summary["player_scores"]["last_game_ago_str"] = time_ago(
        curr_timestamp - score_summary["player_scores"].get("last_game", curr_timestamp)
    )
    score_summary["player_scores"]["last_game_ago"] = curr_timestamp - score_summary[
        "player_scores"
    ].get("last_game", curr_timestamp)

    all_objects_summary = json.loads(r.get(f"all_objects_summary"))

    score_summary["families"] = {}

    for type_name, type_obj in all_objects_summary.items():
        print(type_obj["families"])
        if type_obj["families"].get(player_name):
            score_summary["families"][type_name] = type_obj["families"].get(
                player_name, []
            )

            for code_sha1, family_obj in score_summary["families"][type_name].items():

                family_obj["code"] = highlight(
                    family_obj["code"],
                    PythonLexer(),
                    HtmlFormatter(noclasses=True, linenos="inline", nobackground=True),
                )

    return templates.TemplateResponse(
        request=request,
        name="player.html",
        context={"player_summary": score_summary},
    )


@app.get("/world_map", response_class=HTMLResponse)
async def world_map(request: Request):

    return templates.TemplateResponse(
        request=request, name="world_map.html", context={"types_dict": get_types_dict()}
    )


@app.get("/map_image.png", response_class=Response)
async def get_map_image(request: Request):

    map_image = r.get(f"map_image")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Disposition": "inline; filename=my_image.jpg",
    }
    return Response(content=map_image, media_type="image/png", headers=headers)


@app.get("/hist_counts_image.png", response_class=Response)
async def get_map_image(request: Request):

    counts_historical_plot = r.get(f"counts_historical_plot")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Disposition": "inline; filename=my_image.jpg",
    }
    return Response(
        content=counts_historical_plot, media_type="image/png", headers=headers
    )


@app.get("/refresh_time_plot.png", response_class=Response)
async def refresh_time_plot(request: Request):

    counts_historical_plot = r.get(f"refresh_time_plot")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Disposition": "inline; filename=my_image.jpg",
    }
    return Response(
        content=counts_historical_plot, media_type="image/png", headers=headers
    )


@app.get("/start_game_page", response_class=HTMLResponse)
def start_game_page(request: Request):

    return templates.TemplateResponse(
        request=request, name="start_game_page.html", context={}
    )


@app.get("/play", response_class=HTMLResponse)
def play(request: Request):

    return templates.TemplateResponse(request=request, name="play.html", context={})


@app.post("/create_player")
def create_player(new_user: UserCreate):

    if new_user.verify_password != new_user.password:
        raise HTTPException(status_code=400, detail="Passwords dont match")

    hashed_password = get_password_hash(new_user.password)

    if get_user(new_user.username):
        raise HTTPException(
            status_code=400, detail="User with this username already exists"
        )

    user = User(username=new_user.username, hashed_password=hashed_password)

    user_data = (
        user.model_dump_json() if hasattr(user, "model_dump_json") else user.json()
    )
    r.set(f"player_{user.username}", user_data)

    return {"status": "success"}


@app.post("/control")
def control(
    current_user: Annotated[User, Depends(get_current_active_user)],
    my_keys: KeysPressed,
):
    keys_data = (
        my_keys.model_dump_json()
        if hasattr(my_keys, "model_dump_json")
        else my_keys.json()
    )
    r.set(f"control_{current_user.username}", keys_data)

    return {"status": "success"}


@app.post("/create_bot")
def create_bot(
    current_user: Annotated[User, Depends(get_current_active_user)],
    code: BotCode,
):
    new_bot_data = BotCreate(
        request_type="spectator", spectator_follow_type="object", code=code.code_str
    )
    bot_json = (
        new_bot_data.model_dump_json()
        if hasattr(new_bot_data, "model_dump_json")
        else new_bot_data.json()
    )
    r.set(f"game_{current_user.username}", bot_json)

    return {"status": "success"}


@app.get("/score")
def scores(current_user: Annotated[User, Depends(get_current_active_user)]):

    scores_str = r.get(f"score_{current_user.username}")

    scores = json.loads(scores_str)

    return scores


@app.get("/get_map")
def read_item(
    current_user: Annotated[User, Depends(get_current_active_user)],
    since_epoch: Optional[int] = None,
):

    map_data_str = r.get(f"map_{current_user.username}")

    if not map_data_str:
        map_data = {
            "global_params": {
                "status": "stopped",
                "time_interval": 0.33,
                "map_view_size": 11,
                "epoch": 0,
            },
            "player": {},
            "objects": {},
            "tiles": {},
            "particles": {},
        }
        return map_data

    map_data = json.loads(map_data_str)

    status = map_data["global_params"]["status"]

    # Clients poll faster than the epoch rate; skip resending an unchanged map.
    if (
        status == "running"
        and since_epoch is not None
        and map_data["global_params"].get("epoch") == since_epoch
    ):
        return Response(status_code=204)

    if status == "running":
        unix_timestamp = time.time()
        new_map_timestamp = map_data["global_params"]["new_map_timestamp"]
        map_data["global_params"]["time_left"] = max(
            0.0, new_map_timestamp - unix_timestamp
        )

    return map_data


@app.get("/ping")
def ping(current_user: Annotated[User, Depends(get_current_active_user)]):

    return {"status": "success"}


@app.get("/ping2/{size}")
def ping2(size: int):

    return "a" * size


def _objects_summary_or_empty():
    return json.loads(r.get("all_objects_summary") or "{}")


@app.get("/sitemap.xml")
def sitemap(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="sitemap.xml",
        context={"objects_summary": _objects_summary_or_empty()},
        media_type="application/xml",
    )


@app.get("/robots.txt")
def robots(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="robots.txt",
        context={},
        media_type="text/plain",
    )


@app.get("/llms.txt")
def llms_txt(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="llms.txt",
        context={"objects_summary": _objects_summary_or_empty()},
        media_type="text/markdown",
    )


@app.get("/player_image/{player_name}")
def player_image(request: Request, player_name: str):
    def pick_random_member(class_in, player_name):
        ascii_values_comprehension = [ord(char) for char in player_name]
        rand_seed = sum(ascii_values_comprehension)

        list_len = len(class_in.__dict__["_member_names_"])

        reminder = rand_seed % list_len

        return class_in[class_in.__dict__["_member_names_"][reminder]]

    print(pa.ClothingType.__dict__["_member_names_"])

    svg_data = pa.Avatar(
        style=pick_random_member(pa.AvatarStyle, player_name),
        background_color=pick_random_member(pa.BackgroundColor, player_name),
        top=pick_random_member(pa.HairType, player_name),
        eyebrows=pick_random_member(pa.EyebrowType, player_name),
        eyes=pick_random_member(pa.EyeType, player_name),
        nose=pick_random_member(pa.NoseType, player_name),
        # mouth=pa.MouthType.pick_random(),
        # facial_hair=pa.FacialHairType.pick_random(),
        # Or you can use the colors provided by the library
        hair_color=pick_random_member(pa.HairColor, player_name),
        accessory=pick_random_member(pa.AccessoryType, player_name),
        clothing=pa.ClothingType.GRAPHIC_SHIRT,
        clothing_color=pick_random_member(pa.ClothingColor, player_name),
        shirt_graphic=pa.ClothingGraphic.CUSTOM_TEXT,
        shirt_text=player_name,
    ).render()

    file_bytes = svg_data.encode()

    # Create a BytesIO object from the byte data
    file_like = BytesIO(file_bytes)

    # Set appropriate headers (optional)
    headers = {
        "Cache-Control": "no-cache",
        "Content-Disposition": "inline; filename=my_image.svg",
    }
    return Response(
        content=file_like.getvalue(), media_type="image/svg+xml", headers=headers
    )
