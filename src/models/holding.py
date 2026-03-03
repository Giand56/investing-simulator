from sqlalchemy import Column, ForeignKey, Integer, String

from src.models.base import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String)
    quantity = Column(Integer)