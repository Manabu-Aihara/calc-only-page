from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

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
