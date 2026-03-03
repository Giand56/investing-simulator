from sqlalchemy import Column, Integer, String, Float

from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    cash_balance = Column(Float)
    username = Column(String)