from fastapi import APIRouter, HTTPException, Query
from src.services.stock_service import get_stock_price, get_company_info, get_previous_close, get_daily_pl, \
    get_stock_stats, get_stock_history

router =  APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/{ticker}")
async def get_stocks_price_router(ticker: str):
    return {"ticker" : ticker, "price": round(await get_stock_price(ticker), 2)}

@router.get("/{ticker}/info")
async def get_company_info_router(ticker: str):
    return {"ticker" : ticker, "info": await get_company_info(ticker)}

@router.get("/{ticker}/dailypl")
async def get_daily_pl_router(ticker: str):
    return {"ticker": ticker, "daily_PL": await get_daily_pl(ticker)}

@router.get("/{ticker}/stats")
async def get_daily_pl_router(ticker: str):
    return {"ticker": ticker, "stats": await get_stock_stats(ticker)}

@router.get("/{ticker}/history")
async def stock_history(
    ticker: str,
    period: str = Query(default="1m", enum=["1w", "1m", "3m", "6m", "1y"]),
):
    try:
        return await get_stock_history(ticker, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")