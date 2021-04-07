import io

from PIL import Image
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR, BYTEA, SMALLINT, BOOLEAN

from .database import Base

WIDTH = 600
HEIGHT = 900

blank_img = Image.new("RGB", (WIDTH, HEIGHT), color=(255, 255, 255))
img_byte_arr = io.BytesIO()
blank_img.save(img_byte_arr, format="PNG")
img_byte_arr = img_byte_arr.getvalue()

class Corpse(Base):
    __tablename__ = "corpses"

    corpse_name = Column("corpsename", VARCHAR(40), primary_key=True)
    img = Column("img", BYTEA, default=img_byte_arr)
    stage = Column("stage", SMALLINT, default=2)
    is_open = Column("open", BOOLEAN, default=False)