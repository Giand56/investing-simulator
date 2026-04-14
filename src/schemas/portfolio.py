from typing import List

from pydantic import BaseModel

from src.models import holding


class TradeOrder(BaseModel):
    ticker: str
    quantity: float

class Holding(BaseModel):
    ticker: str
    quantity: float

class BuyResponse(BaseModel):
    success: bool
    message: str
    ticker: str | None = None
    quantity: float | None = None
    total_cost: float | None = None

class SellResponse(BaseModel):
    success: bool
    message: str
    ticker: str | None = None
    quantity: float | None = None
    total_value: float | None = None

class HoldingResponse(BaseModel):
    ticker: str
    name: str
    price: float
    priceChange: float

class SectorAllocation(BaseModel):
    name: str
    value: float

class PortfolioResponse(BaseModel):
    username: str
    cash_balance: float
    portfolio_value: float
    overall_performance: float
    overall_performance_percent: float
    daily_PL: float
    daily_PL_percent: float
    sector_allocation: List[SectorAllocation]
    holdings: List[HoldingResponse]

class DetailedHoldingResponse(BaseModel):
    quantity: float
    currentPrice: float
    buyInPrice: float
    changeSinceBuy: float