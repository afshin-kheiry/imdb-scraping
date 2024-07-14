from base.database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
