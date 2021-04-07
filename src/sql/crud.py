from sqlalchemy.orm import Session
import random

from . import models, schemas


def get_corpse(db: Session, corpse_name: str):
    return (db.query(models.Corpse)
            .filter(models.Corpse.corpse_name == corpse_name)
            .first())

def create_corpse(db: Session, corpse_name: str, img: bytes):
    db_corpse = models.Corpse(corpse_name=corpse_name, img=img)
    db.add(db_corpse)
    db.commit()
    db.refresh(db_corpse)
    return db_corpse

def update_corpse(db: Session, corpse_name: str, img: bytes):
    db_corpse = get_corpse(db, corpse_name=corpse_name)
    if db_corpse and db_corpse.stage < 4:
        db_corpse.img = img
        db_corpse.is_open = False
        db_corpse.stage = db_corpse.stage + 1 # musn't use +=
        db.commit()
        return (True, db_corpse)
    return (False, db_corpse)

def get_num_corpses(db: Session, complete: bool = False) -> int:
    if complete:
        filter_by = models.Corpse.stage == 4
    else:
        filter_by = models.Corpse.stage < 4
    return (db.query(models.Corpse)
            .filter(filter_by)
            .count())

def close_corpse(db: Session, corpse_name: str):
    db_corpse = get_corpse(db, corpse_name=corpse_name)
    if db_corpse:
        db_corpse.open = False
        db.commit()
        return True
    return False

def get_rand_incomplete_corpses(db: Session, n: int):
    incomplete = (db.query(models.Corpse)
        .filter(models.Corpse.stage < 4, ~models.Corpse.is_open)
        .values(models.Corpse.corpse_name, models.Corpse.stage))
    incomplete = list(incomplete)
    if n > len(incomplete):
        n = len(incomplete)
    sample = random.sample(list(incomplete), n)
    return sample

def get_rand_complete_corpse(db: Session):
    complete = (db.query(models.Corpse)
        .filter(models.Corpse.stage >= 4)
        .values(models.Corpse.corpse_name))
    complete = list(complete)
    choice = random.choice(list(complete))
    return choice.corpse_name

def get_stage(db: Session, corpse_name: str):
    db_corpse = get_corpse(db, corpse_name=corpse_name)
    return db_corpse.stage if db_corpse else -1