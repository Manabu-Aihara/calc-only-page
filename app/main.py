from pydantic import BaseModel
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt
from jose.exceptions import JWTClaimsError

from . import models
from .database_base import session, engine
from .dataframe_collect_lib import put_vertical_dataframe

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        yield session
    finally:
        session.close()


@app.get("/frame-data/{team_code}")
def get_calclated_data(team_code: str, session: Session = Depends(get_db)):
    result_df = put_vertical_dataframe(team_code=int(team_code))
    return result_df.to_dict()


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


def get_user(user_id: int):
    return (
        session.query(models.StaffLogin)
        .filter(models.StaffLogin.STAFFID == user_id)
        .first()
    )


def authenticate_user(user_id: int, password: str):
    login_user = get_user(user_id)
    if login_user.check_password(password) is False:
        return False
    else:
        return login_user


async def decord_token_data(token: str = Depends(oauth2_scheme)):
    # async def decord_token_data(token: str):
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
    except JWTClaimsError as e:
        print(f"Pass 2: {e}")
        raise credentials_exception
    except Exception as e:
        print(e)
    if user_id is None:
        print("Pass 3")
        raise credentials_exception
    return user_id


token_store = {}


@app.get("/users/me")
async def read_users_me(request: Request):
    param_token = request.query_params.get("token")

    # トークンを一時的に保存
    token_store[param_token] = param_token

    # リダイレクト時にトークンIDのみを渡す
    return RedirectResponse(
        url=f"/receive-data?token_id={param_token}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# Fastapi : jinja2.exceptions.TemplateNotFound
# https://stackoverflow.com/questions/67668606/fastapi-jinja2-exceptions-templatenotfound-index-html
BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))


@app.get("/receive-data")
async def receive_data(request: Request):
    token_id = request.query_params.get("token_id")
    if not token_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token ID is missing"
        )

    # 保存されたトークンを取得
    token = token_store.get(token_id)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token ID"
        )

    # トークンを検証
    try:
        user_id = await decord_token_data(token)
        # 使用済みトークンを削除
        del token_store[token_id]
        user_info = (
            session.query(models.User.LKANA)
            .filter(models.User.STAFFID == user_id)
            .first()
        )
        team_code_list = session.query(models.Team.CODE).all()
        # return {"user id": user_id}
        return templates.TemplateResponse(
            "select_form.html",
            {"name": user_info.LKANA, "team_nums": team_code_list, "request": request},
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@app.post("/collect-members-data")
async def post_collected_dict(request: Request, team_number: str = Form(...)):
    # return {"team code": team_number}
    result_df = put_vertical_dataframe(team_code=int(team_number))
    return result_df.to_html()
