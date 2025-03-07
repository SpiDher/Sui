from db import Base 
from sqlalchemy import String
from sqlalchemy.orm import mapped_column,Mapped


class BaseUser(Base):
    id:Mapped[int]=mapped_column('id',primary_key=True,autoincrement=True)
    username:Mapped[str]=mapped_column(String(50),unique=True)
    pin:Mapped[str]=mapped_column(String,nullable=False)