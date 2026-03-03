from typing import List

from pydantic import BaseModel

from src.models import holding


class TradeOrder(BaseModel):
    user_id: int
    ticker: str
    quantity: int

class Holding(BaseModel):
    ticker: str
    quantity: int

class BuyResponse(BaseModel):
    success: bool
    message: str
    ticker: str | None = None
    quantity: int | None = None
    total_cost: float | None = None

class SellResponse(BaseModel):
    success: bool
    message: str
    ticker: str | None = None
    quantity: int | None = None
    total_value: float | None = None

class HoldingResponse(BaseModel):
    ticker: str
    quantity: int
    total_value: float

class PortfolioResponse(BaseModel):
    username: str
    cash_balance: float
    portfolio_value: float
    holdings: List[HoldingResponse]