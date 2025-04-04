from datetime import datetime, timedelta, timezone
from typing import Union

from jose import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from jose.exceptions import JWTClaimsError
from pydantic import BaseModel

from .database_base import session
from .models import StaffLogin
from .dataframe_collect_lib import put_vertical_dataframe

# パスワード（およびハッシュ化）によるOAuth2、JWTトークンによるBearer
# https://fastapi.tiangolo.com/ja/tutorial/security/oauth2-jwt/#jwt_1

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "78b2ec4498fb06ca2c98f31a31deea66b68264c55f7d76ef0c35a571bde95276"
SECRET_KEY = "you-will-never-guess"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def get_user(user_id: int):
    return session.query(StaffLogin).filter(StaffLogin.STAFFID == user_id).first()


def authenticate_user(user_id: int, password: str):
    login_user = get_user(user_id)
    if login_user.check_password(password) is False:
        return False
    else:
        return login_user


# 結局これもテスト用の
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# こっちはだめだった
# async def decord_token_data(token: str = Depends(oauth2_scheme)):
async def decord_token_data(token: str):
    print(f"Token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = 0
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            print("Pass 1")
            raise credentials_exception
        # token_data = TokenData(user_id=user_id)
    except JWTClaimsError as e:
        print(f"Pass 2: {e}")
        raise credentials_exception
    user = get_user(user_id=user_id)
    if user is None:
        print("Pass 3")
        raise credentials_exception
    return user


# トークン認証、テスト用
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = authenticate_user(int(form_data.username), form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.STAFFID)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/users/me")
async def read_users_me(
    token: str,
    current_user: StaffLogin = Depends(dependency=decord_token_data),
):
    # return current_user, token
    return RedirectResponse(f"/frame-data/{current_user.STAFFID}")


# @app.exception_handler(RequestValidationError)
# async def handler(request: Request, exc: RequestValidationError):
#     print(exc)
#     return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/frame-data/{user_id}")
def get_calclated_data(
    user_id: int,
    current_user: StaffLogin = Depends(dependency=decord_token_data),
):
    result_df = put_vertical_dataframe(team_code=2)
    return result_df.to_dict(), user_id
