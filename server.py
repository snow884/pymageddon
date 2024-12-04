import json
import time
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import redis
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


class KeysPressed(BaseModel):
    ArrowRight: bool
    ArrowLeft: bool
    ArrowDown: bool
    ArrowUp: bool


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


class UserLogin(BaseModel):
    username: str
    password: str


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


@app.get("/login_page")
def login_page():
    with open("login.html") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)


@app.get("/create_player_page")
def create_user_page():
    with open("create_user.html") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/")
def index():
    with open("index.html") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)


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


@app.get("/get_map")
def read_item(current_user: Annotated[User, Depends(get_current_active_user)]):

    map_data_str = r.get(f"map_{current_user.username}")
    map_data = json.loads(map_data_str)

    unix_timestamp = time.time()
    new_map_timestamp = map_data["global_params"]["new_map_timestamp"]

    timestamp = map_data["global_params"]["timestamp"]
    print(new_map_timestamp - unix_timestamp)
    map_data["global_params"]["time_left"] = new_map_timestamp - unix_timestamp

    return map_data


@app.get("/ping")
def read_item(current_user: Annotated[User, Depends(get_current_active_user)]):

    return {"status": "success"}
