from src.database import SessionLocal
from src.models.holding import Holding
from src.models.user import User
from src.schemas.test_schemas import TestUser
from src.services.stock_service import get_stock_price
from src.auth import hash_password

def buy(ticker: str, quantity: int, user_id: int):
    price = get_stock_price(ticker)
    if price is None:
        return{"success": False, "message": "stock does not exist"}
    db = SessionLocal()
    total_price = price * quantity
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
                new_holding = Holding(ticker = ticker, quantity = quantity, user_id = user_id)
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

def sell(ticker: str, quantity: int, user_id: int):
    price = get_stock_price(ticker)
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

def get_info(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"error": "User not found"}
        holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
        total_value = 0.0
        holdings_list = []
        for h in holdings:
            stock_value = get_stock_price(h.ticker) or 0.0
            holdings_list.append({"ticker": h.ticker,
                                  "quantity": h.quantity,
                                  "total_value": round(stock_value*h.quantity,2)})
            total_value += stock_value*h.quantity

        return {"username": user.username,
                "cash_balance": round(user.cash_balance, 2),
                "portfolio_value": round(total_value, 2),
                "holdings": holdings_list}
    finally:
        db.close()