from pydantic import BaseModel

class CorpseBase(BaseModel):
    pass

class CorpseCreate(CorpseBase):
    corpse_name: str
    img: bytes

class CorpseUpdate(CorpseBase):
    img: bytes

class Corpse(CorpseBase):
    stage: int
    is_open: bool

    class Config:
        orm_mode = True