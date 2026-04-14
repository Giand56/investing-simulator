from fastapi import APIRouter, HTTPException, Query, Depends

from src.auth import get_current_user
from src.schemas.stocks import Trending
from src.services.stock_service import get_stock_price, get_company_info, get_previous_close, get_daily_pl, \
    get_stock_stats, get_stock_history, get_trending_stocks, get_holding_stats, get_specific_holding

router =  APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/trending", response_model=Trending)
async def get_trending_router():
    trending = await get_trending_stocks()
    if trending is None:
        raise HTTPException(status_code=404, detail="error 404")
    return trending

@router.get("/{ticker}/shortstats")
async def get_holding_stats_router(ticker: str):
    stats = await get_holding_stats(ticker)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return stats

@router.get("/{ticker}/holding")
async def get_specific_holding_router(ticker: str, current_user=Depends(get_current_user)):
    stats = await get_specific_holding(ticker, current_user.id)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"either not authenticated, '{ticker}' not found or no holding existent of the stock.")
    return stats

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

@router.get("/{ticker}/history")
async def stock_history(
    ticker: str,
    period: str = Query(default="1m", enum=["1w", "1m", "3m", "6m", "1y"]),
):
    data = await get_stock_history(ticker, period)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return data