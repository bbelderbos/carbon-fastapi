from datetime import datetime, timedelta
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise

from .images import create_carbon_image
from .db import get_user, create_user

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    or 30)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str
    password2: str


class CarbonPayload(BaseModel):
    code: str
    parameters: dict[str, str] = {}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/images", status_code=201, response_class=FileResponse)
async def create_code_image(payload: CarbonPayload,
                            current_user: User = Depends(get_current_user)):
    ret = await create_carbon_image(payload.code, **payload.parameters)
    return ret


@app.post("/users", status_code=201, response_model=User)
async def signup(payload: UserCreate):
    """Create a new user in the database"""
    username = payload.username
    password = payload.password
    password2 = payload.password2

    user = await get_user(username)
    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    if password != password2:
        raise HTTPException(
            status_code=400,
            detail="The two passwords should match",
        )

    # TODO: could also check password strength

    ret = await create_user(username, password)
    return ret


register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL"),
    modules={"models": ["src.db"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
