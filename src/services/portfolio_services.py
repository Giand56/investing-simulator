import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.database import SessionLocal
from src.models.holding import Holding
from src.models.user import User
from src.schemas.test_schemas import TestUser
from src.services.stock_service import get_stock_price, get_daily_pl, get_daily_pl_percent, get_company_info
from src.auth import hash_password

async def buy(ticker: str, quantity: int, user_id: int):
    price = await get_stock_price(ticker)
    if price is None:
        return{"success": False, "message": "stock does not exist"}
    db = SessionLocal()
    total_price = round(price * quantity, 2)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"success": False, "message": "User does not exist"}
        if user.cash_balance >= total_price:
            user.cash_balance -= total_price
            holding = (db.query(Holding).filter
                       (Holding.user_id == user_id, Holding.ticker == ticker).first())
            if holding is not None:
                holding.quantity += quantity
            else:
                new_holding = Holding(ticker = ticker,
                                      quantity = quantity,
                                      user_id = user_id,
                                      buy_in_price = total_price)
                db.add(new_holding)
            db.commit()
            return {"success": True,
                    "message": "Buy order has been placed",
                    "ticker": ticker,
                    "quantity": quantity,
                    "total_cost": total_price}
        else:
            return {"success": False, "message": "Not enough cash in portfolio"}
    finally:
        db.close()

async def sell(ticker: str, quantity: int, user_id: int):
    price = await get_stock_price(ticker)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"success": False, "message": "User does not exist"}
        holding = (db.query(Holding).filter
                   (Holding.user_id == user_id, Holding.ticker == ticker).first())
        if holding is not None:
            if holding.quantity >= quantity:
                holding.quantity -= quantity
                user.cash_balance += quantity*price
                if holding.quantity == 0:
                    db.delete(holding)
                db.commit()
                return {"success": True,
                        "message": "Sell order has been placed",
                        "ticker": ticker,
                        "quantity": quantity,
                        "total_cost": round(price*quantity, 2)}
            else:
                return {"success": False, "message": "You don't own that many stocks"}
        else:
            return {"success": False, "message": "this stock is not in your portfolio"}
    finally:
        db.close()

async def get_sector_allocation(total_value: float, holdings_list: list[dict]) -> list[dict]:
    tickers = [h["ticker"] for h in holdings_list]

    infos = await asyncio.gather(*[get_company_info(t) for t in tickers])

    sector_totals: dict[str, float] = {}
    for h, info in zip(holdings_list, infos):
        sector = info.get("sector", "Unknown")
        pct = (h["total_value"] / total_value) * 100
        sector_totals[sector] = sector_totals.get(sector, 0.0) + pct

    stock_total = sum(sector_totals.values())
    sector_totals["Cash"] = 100.0 - stock_total

    return [
        {"name": name, "value": round(value, 2)}
        for name, value in sector_totals.items()
    ]


async def get_info(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"error": "User not found"}

        holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
        tickers = [h.ticker for h in holdings]

        # fire all yfinance calls at once
        prices, daily_pls, daily_pl_percents = await asyncio.gather(
            asyncio.gather(*[get_stock_price(t) for t in tickers]),
            asyncio.gather(*[get_daily_pl(t) for t in tickers]),
            asyncio.gather(*[get_daily_pl_percent(t) for t in tickers]),
        )

        total_value = float(user.cash_balance)
        buy_in_value = float(user.cash_balance)
        holdings_list = []

        for h, price, in zip(holdings, prices):
            price = price or 0.0
            stock_total = price * h.quantity
            total_value += stock_total
            buy_in_value += float(h.buy_in_price)
            holdings_list.append({
                "ticker": h.ticker,
                "quantity": h.quantity,
                "total_value": round(stock_total, 2)
            })

        overall_performance = total_value - buy_in_value
        overall_performance_percent = ((total_value / buy_in_value) - 1) * 100 if buy_in_value > 0 else 0

        daily_pl = sum(v for v in daily_pls if v) / len(holdings) if holdings else 0.0
        daily_pl_percent = sum(v for v in daily_pl_percents if v) / len(holdings) if holdings else 0.0

        sector_allocation = await get_sector_allocation(total_value, holdings_list)

        return {
            "username": user.username,
            "cash_balance": round(float(user.cash_balance), 2),
            "portfolio_value": round(total_value, 2),
            "overall_performance": round(overall_performance, 2),
            "overall_performance_percent": round(overall_performance_percent, 2),
            "daily_PL": round(daily_pl, 2),
            "daily_PL_percent": round(daily_pl_percent, 2),
            "sector_allocation": sector_allocation,
            "holdings": holdings_list
        }
    finally:
        db.close()
