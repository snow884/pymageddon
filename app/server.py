import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
import redis
from common_utils.utils import get_types_dict
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 31

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0)

origins = [
    "http://localhost:8000",  # Your frontend's origin
    "http://localhost:8000",  # Replace with your frontend's port if different
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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


@app.get("/explorer/family/{family}", response_class=HTMLResponse)
async def explorer_family(request: Request):

    with open("objects_summary.json") as f:
        objects_summary = json.load(f)

    map_image = r.get(f"objects_summary")

    return templates.TemplateResponse(
        request=request,
        name="explorer.html",
        context={"all_objects_summary": all_objects_summary},
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

    r.set(f"player_{user.username}", user.json())

    return {"status": "success"}


@app.post("/control")
def control(
    current_user: Annotated[User, Depends(get_current_active_user)],
    my_keys: KeysPressed,
):

    r.set(f"control_{current_user.username}", my_keys.json())

    return {"status": "success"}


@app.post("/create_bot")
def create_bot(
    current_user: Annotated[User, Depends(get_current_active_user)],
    code: BotCode,
):
    print(code.code_str)
    new_bot_data = BotCreate(
        request_type="spectator", spectator_follow_type="object", code=code.code_str
    )
    print(new_bot_data.json())
    r.set(f"game_{current_user.username}", new_bot_data.json())

    return {"status": "success"}


@app.get("/score")
def scores(current_user: Annotated[User, Depends(get_current_active_user)]):

    scores_str = r.get(f"score_{current_user.username}")

    scores = json.loads(scores_str)

    return scores


@app.get("/get_map")
def read_item(current_user: Annotated[User, Depends(get_current_active_user)]):

    # time.sleep(0.1)

    map_data_str = r.get(f"map_{current_user.username}")

    if not map_data_str:
        map_data = {
            "global_params": {
                "status": "stopped",
                "time_interval": 1,
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

    if status == "running":

        unix_timestamp = time.time()
        new_map_timestamp = map_data["global_params"]["new_map_timestamp"]

        timestamp = map_data["global_params"]["timestamp"]
        print(new_map_timestamp - unix_timestamp)
        map_data["global_params"]["time_left"] = new_map_timestamp - unix_timestamp

    return map_data


@app.get("/ping")
def read_item(current_user: Annotated[User, Depends(get_current_active_user)]):

    return {"status": "success"}


@app.get("/sitemap.xml")
def sitemap(request: Request):
    objects_summary = json.loads(r.get(f"all_objects_summary"))

    return templates.TemplateResponse(
        request=request,
        name="sitemap.xml",
        context={"objects_summary": objects_summary},
    )


@app.get("/robots.txt")
def robots(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="robots.txt",
        context={},
    )
