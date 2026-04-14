from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Float

from src.models.base import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String)
    quantity = Column(Float)
    buy_in_price = Column(Numeric(10, 2))