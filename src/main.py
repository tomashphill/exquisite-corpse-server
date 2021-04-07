import base64
from enum import Enum
import io


from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic.main import BaseModel
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session


from .sql import crud, models, schemas
from .sql.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def from_data_url(s: str):
    """
    Converts dataURL into base64 bytes
    """
    return base64.decodestring(s.split(',')[1].encode())


@app.get("/corpse-name-taken/{corpse_name}", response_model=bool)
def name_taken(corpse_name: str, 
                db: Session = Depends(get_db)):
    db_corpse = crud.get_corpse(db, corpse_name=corpse_name)
    return True if db_corpse else False


class CorpseStatus(str, Enum):
    complete = "complete"
    incomplete = "incomplete"

@app.get("/num-of-completed/{status}", response_model=int)
def num_of_corpses(status: CorpseStatus, db: Session = Depends(get_db)):
    if status == CorpseStatus.complete:
        return crud.get_num_corpses(db, complete=True)
    elif status == CorpseStatus.incomplete:
        return crud.get_num_corpses(db)
    else:
        raise HTTPException(status_code=404, detail="Invalid Parameter")


class Image(BaseModel):
    data: str

@app.post("/create-corpse/{corpse_name}", status_code=201)
def create_corpse(corpse_name: str, img: Image, db: Session = Depends(get_db)):
    db_corpse = crud.get_corpse(db, corpse_name=corpse_name)
    if db_corpse:
        raise HTTPException(status_code=404, detail="Corpse already created")
    png_b = from_data_url(img.data)
    crud.create_corpse(db, corpse_name, png_b)
    return f'{corpse_name} is ready for its body to be drawn!'


@app.post("/update-corpse/{corpse_name}", status_code=200)
def update_corpse(corpse_name: str, img: Image, db: Session = Depends(get_db)):
    png_b = from_data_url(img.data)
    is_successful, db_corpse = crud.update_corpse(db, corpse_name, png_b)
    if is_successful:
        s = db_corpse.stage
        if s == 3:
            return f"{db_corpse.corpse_name} is ready for its legs to be drawn!"
        elif s == 4:
            return f"{db_corpse.corpse_name} is complete! Time to release it into the wild."
    else:
        raise HTTPException(status_code=403, detail="Cannot update corpse!")


@app.get("/corpses/{corpse_name}", responses={200: {"content":{"image/png":{}}}})
def get_corpse_img(corpse_name: str, db: Session = Depends(get_db)):
    db_corpse = crud.get_corpse(db, corpse_name=corpse_name)
    if db_corpse is None:
        raise HTTPException(status_code=404, detail="Corpse not found")
    elif db_corpse.stage < 4 and db_corpse.is_open:
        raise HTTPException(status_code=403, detail="Corpse opened by another corpse creater")
    print(db_corpse.img[:50])
    return StreamingResponse(io.BytesIO(db_corpse.img), media_type="image/png")


@app.get("/close/{corpse_name}")
def close_corpse(corpse_name: str, db: Session = Depends(get_db)):
    is_successful = crud.close_corpse(db, corpse_name=corpse_name)
    return "Close" if is_successful else "Unopened"


@app.get("/random_incomplete_corpses/{num}")
def get_random_incomplete_corpses(num: int, db: Session = Depends(get_db)):
    corpses = crud.get_rand_incomplete_corpses(db, num)
    return corpses


@app.get("/random-complete-corpse/")
def get_random_complete_corpse(db: Session = Depends(get_db)):
    corpse = crud.get_rand_complete_corpse(db)
    return corpse


@app.get("/stage/{corpse_name}")
def get_corpse_stage(corpse_name: str, db: Session = Depends(get_db)):
    return crud.get_stage(db, corpse_name=corpse_name)