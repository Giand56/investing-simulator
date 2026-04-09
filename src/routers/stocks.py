from fastapi import APIRouter, HTTPException, Query
from src.services.stock_service import get_stock_price, get_company_info, get_previous_close, get_daily_pl, \
    get_stock_stats, get_stock_history

router =  APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/{ticker}")
async def get_stocks_price_router(ticker: str):
    price = await get_stock_price(ticker)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return {"ticker": ticker, "price": price}

@router.get("/{ticker}/info")
async def get_company_info_router(ticker: str):
    info = await get_company_info(ticker)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return {"ticker": ticker, "info": info}

@router.get("/{ticker}/stats")
async def get_stock_stats_router(ticker: str):
    stats = await get_stock_stats(ticker)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return {"ticker": ticker, "stats": stats}

@router.get("/{ticker}/dailypl")
async def get_daily_pl_router(ticker: str):
    daily_pl = await get_daily_pl(ticker)
    if daily_pl is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return {"ticker": ticker, "daily_PL": daily_pl}

@router.get("/{ticker}/history")
async def stock_history(
    ticker: str,
    period: str = Query(default="1m", enum=["1w", "1m", "3m", "6m", "1y"]),
):
    data = await get_stock_history(ticker, period)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return data