from src.schemas.portfolio import TradeOrder
from fastapi import APIRouter

from src.schemas.test_schemas import TestUser
from src.services.portfolio_services import buy, sell, get_info, create_user

router =  APIRouter()


@router.post("/userAdd")
def add_user(user: TestUser):
    return create_user(user)
@router.post("/buy")
def buy_order(order: TradeOrder):
    return buy(order.ticker, order.quantity, order.user_id)

@router.post("/sell")
def sell_order(order: TradeOrder):
    return sell(order.ticker, order.quantity, order.user_id)

@router.get("/portfolio")
def get_portfolio(user_id: int):
    return get_info(user_id)