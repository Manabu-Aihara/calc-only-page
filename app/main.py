from pydantic import BaseModel
from pathlib import Path
import uuid
from datetime import datetime

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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_id")


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
        print(f"func: {e}")
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
    # 303 See Other - Must
    # https://stackoverflow.com/questions/73076517/how-to-send-redirectresponse-from-a-post-to-a-get-route-in-fastapi
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
    # リダイレクトがダメなのかなぁ？
    # async def receive_data(request: Request, 🙅‍♀user_id: int = Depends(decord_token_data)):
    token_id = request.query_params.get("token_id")

    # 保存されたトークンを取得
    stored_token = token_store.get(token_id)
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token ID"
        )
    # トークンを検証
    try:
        user_id = await decord_token_data(stored_token)
        print(f"ID: {user_id}")
        # return {"user id": user_id}
        user_info = (
            session.query(models.User.LKANA)
            .filter(models.User.STAFFID == user_id)
            .first()
        )
        team_code_list = session.query(models.Team.CODE).all()

        # 新しいトークンIDを生成
        new_token_id = str(uuid.uuid4())
        # ?
        token_store[new_token_id] = {"token": stored_token}
        print(f"Token new or old: {token_store[new_token_id]}")

        # 使用済みトークンを削除
        del token_store[stored_token]

        return templates.TemplateResponse(
            "select_form.html",
            {
                "request": request,
                "name": user_info.LKANA,
                "team_nums": team_code_list,
                "new_token": new_token_id,
            },
        )
    except Exception as e:
        print(f"app: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@app.post("/collect-members-data")
async def post_collected_dict(request: Request, team_number: str = Form(...)):
    result_df = put_vertical_dataframe(team_code=int(team_number))
    return result_df.T.to_dict()


@app.post("/collect-members-html")
async def output_collected_html(
    request: Request, team_number: str = Form(...), form_token: str = Form(...)
):
    # team_number = form_data.team_number
    print(f"Form token: {form_token}")
    result_df = put_vertical_dataframe(team_code=int(team_number))
    setup_html = """
    <!DOCTYPE html>
    <html>

    <head>
        <link rel="stylesheet" href="https://cdn.datatables.net/2.2.2/css/dataTables.dataTables.css" />

        <script src="https://code.jquery.com/jquery-3.7.1.min.js"
            integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
        <script src="https://cdn.datatables.net/2.2.2/js/dataTables.js"></script>
        <script>
            $(document).ready(function () {
                $('.dataframe').DataTable();
            });
        </script>
    </head>

    <body>
        <div>
    """
    table_tag_html = result_df.T.to_html()
    teardown_html = """
        </div>
    </body>

    </html>
    """
    output_html = setup_html + table_tag_html + teardown_html
    dateime_format = datetime.today().strftime("%Y%m%d%H%M")
    file_name = f"{team_number}-{dateime_format}"

    # https://note.nkmk.me/python-pathlib-file-open-read-write-unlink/
    # 新規ファイルを作成する場合は直上のディレクトリまでは作成しておく必要がある。
    out_path = Path(f"app/templates/output_{file_name}.html")
    with out_path.open(mode="w") as f:
        f.write(output_html)

    return RedirectResponse(
        f"/output-table?file_name={file_name}&token_id={form_token}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/output-table")
def display_table(request: Request):
    token_id = request.query_params.get("token_id")
    if not token_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token ID is missing"
        )
    group_and_date = request.query_params.get("file_name")
    del token_store[token_id]
    return templates.TemplateResponse(
        f"output_{group_and_date}.html", {"request": request}
    )
