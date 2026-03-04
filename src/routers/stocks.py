from fastapi import APIRouter
from src.services.stock_service import get_stock_price

router =  APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/stocks/{ticker}")
def get_stocks(ticker: str):
    return {"ticker" : ticker, "price": get_stock_price(ticker)}