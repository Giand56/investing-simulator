from src.auth import get_current_user
from src.schemas.portfolio import TradeOrder, BuyResponse, SellResponse, PortfolioResponse
from fastapi import APIRouter, Depends

from src.schemas.test_schemas import TestUser
from src.services.portfolio_services import buy, sell, get_info

router =  APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/buy", response_model=BuyResponse)
def buy_order(order: TradeOrder, current_user = Depends(get_current_user)):
    return buy(order.ticker, order.quantity, current_user.id)

@router.post("/sell", response_model=SellResponse)
def sell_order(order: TradeOrder, current_user = Depends(get_current_user)):
    return sell(order.ticker, order.quantity, current_user.id)

@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(current_user = Depends(get_current_user)):
    return get_info(current_user.id)