import asyncio

from src.database import SessionLocal
from src.models.holding import Holding
from src.models.user import User
from src.services.stock_service import get_stock_price, get_daily_pl, get_daily_pl_percent, get_company_info, \
    get_holding_stats


async def buy(ticker: str, quantity: float, user_id: int):
    price = await get_stock_price(ticker)
    if price is None:
        return {"success": False, "message": "Stock does not exist"}
    db = SessionLocal()
    total_price = round(price * quantity, 2)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"success": False, "message": "User does not exist"}
        if user.cash_balance < total_price:
            return {"success": False, "message": "Not enough cash in portfolio"}

        user.cash_balance -= total_price
        holding = db.query(Holding).filter(
            Holding.user_id == user_id, Holding.ticker == ticker
        ).first()

        if holding is not None:
            old_total = float(holding.buy_in_price) * holding.quantity
            new_total = old_total + total_price
            holding.quantity += quantity
            holding.buy_in_price = new_total / holding.quantity
        else:
            db.add(Holding(
                ticker=ticker,
                quantity=quantity,
                user_id=user_id,
                buy_in_price=price
            ))
        db.commit()
        return {
            "success": True,
            "message": "Buy order has been placed",
            "ticker": ticker,
            "quantity": quantity,
            "total_cost": total_price
        }
    finally:
        db.close()


async def sell(ticker: str, quantity: float, user_id: int):
    price = await get_stock_price(ticker)
    if price is None:
        return {"success": False, "message": "Stock does not exist"}
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"success": False, "message": "User does not exist"}

        holding = db.query(Holding).filter(
            Holding.user_id == user_id, Holding.ticker == ticker
        ).first()
        if holding is None:
            return {"success": False, "message": "This stock is not in your portfolio"}
        if holding.quantity < quantity:
            return {"success": False, "message": "You don't own that many stocks"}

        holding.quantity -= quantity
        user.cash_balance += quantity * price
        if holding.quantity == 0:
            db.delete(holding)
        db.commit()
        return {
            "success": True,
            "message": "Sell order has been placed",
            "ticker": ticker,
            "quantity": quantity,
            "total_cost": round(price * quantity, 2)
        }
    finally:
        db.close()


async def get_sector_allocation(total_value: float, holdings_list: list[dict]) -> list[dict]:
    tickers = [h["ticker"] for h in holdings_list]
    infos = await asyncio.gather(*[get_company_info(t) for t in tickers])

    sector_totals: dict[str, float] = {}
    for h, info in zip(holdings_list, infos):
        sector = info.get("sector") if info else None
        sector = sector or "Unknown"
        pct = (h["price"] / total_value) * 100
        sector_totals[sector] = sector_totals.get(sector, 0.0) + pct

    stock_total = sum(sector_totals.values())
    sector_totals["Cash"] = 100.0 - stock_total

    return [
        {"name": name, "value": round(value, 2)}
        for name, value in sector_totals.items()
    ]


async def get_info(user_id: int) -> dict | None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
        tickers = [h.ticker for h in holdings]

        stats_list = await asyncio.gather(*[get_holding_stats(t) for t in tickers])

        total_value = float(user.cash_balance)
        buy_in_value = float(user.cash_balance)
        daily_pl_values = []
        daily_pl_percent_values = []
        holdings_list = []

        for h, stats in zip(holdings, stats_list):
            stats = stats or {}
            price = stats.get("price", 0.0)
            stock_total = price * h.quantity
            total_value += stock_total
            buy_in_value += float(h.buy_in_price) * h.quantity
            daily_pl_values.append(stats.get("daily_pl", 0.0))
            daily_pl_percent_values.append(stats.get("daily_pl_percent", 0.0))
            holdings_list.append({
                "ticker": h.ticker,
                "name": stats.get("name", h.ticker),
                "quantity": h.quantity,
                "price": round(stock_total, 2),
                "priceChange": round(stats.get("daily_pl_percent", 0.0), 2)
            })

        overall_performance = total_value - buy_in_value
        overall_performance_percent = ((total_value / buy_in_value) - 1) * 100 if buy_in_value > 0 else 0

        daily_pl = sum(daily_pl_values) / len(daily_pl_values) if daily_pl_values else 0.0
        daily_pl_percent = sum(daily_pl_percent_values) / len(daily_pl_percent_values) if daily_pl_percent_values else 0.0

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