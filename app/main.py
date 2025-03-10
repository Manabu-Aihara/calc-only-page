from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import models
from .database_base import session, engine

from .series_to_frame import put_vertical_dataframe

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        yield session
    finally:
        session.close()


@app.get("/frame-data/{part_flag}")
def get_calclated_data(part_flag: int, session: Session = Depends(get_db)):
    result_df = put_vertical_dataframe(part_flag=part_flag)
    return result_df.to_dict()
