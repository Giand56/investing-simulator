from fastapi import APIRouter, Depends, HTTPException

from src.auth import get_current_user
from src.schemas.portfolio import TradeOrder, BuyResponse, SellResponse, PortfolioResponse, DetailedHoldingResponse
from src.services.portfolio_services import buy, sell, get_info

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/buy", response_model=BuyResponse)
async def buy_order(order: TradeOrder, current_user=Depends(get_current_user)):
    return await buy(order.ticker, order.quantity, current_user.id)


@router.post("/sell", response_model=SellResponse)
async def sell_order(order: TradeOrder, current_user=Depends(get_current_user)):
    return await sell(order.ticker, order.quantity, current_user.id)

@router.get("/holding/{ticker}", response_model=DetailedHoldingResponse)

@router.get("/", response_model=PortfolioResponse)
async def get_portfolio(current_user=Depends(get_current_user)):
    data = await get_info(current_user.id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data