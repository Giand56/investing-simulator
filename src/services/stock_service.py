import asyncio
import yfinance as yf

from src.database import SessionLocal
from src.models.holding import Holding
from src.models.user import User

PERIOD_MAP = {
    "1w": "7d",
    "1m": "1mo",
    "3m": "3mo",
    "6m": "6mo",
    "1y": "1y",
}


async def get_stock_price(ticker: str) -> float | None:
    def _fetch():
        try:
            stock = yf.Ticker(ticker)
            price = stock.fast_info["last_price"]
            return round(price, 2)
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)


async def get_stock_history(ticker: str, period: str) -> dict | None:
    def _fetch():
        try:
            if period not in PERIOD_MAP:
                raise ValueError(f"Invalid period '{period}'. Choose from: {list(PERIOD_MAP.keys())}")

            stock = yf.Ticker(ticker)
            hist = stock.history(period=PERIOD_MAP[period], interval="1h" if period == "1w" else "1d")

            if hist.empty:
                return None

            data = [
                {
                    "date": index.strftime("%b %-d") if period in ("1w", "1m", "3m") else index.strftime("%b %-d '%y"),
                    "price": round(row["Close"], 2),
                }
                for index, row in hist.iterrows()
            ]

            return {"ticker": ticker.upper(), "period": period, "data": data}
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)


async def get_company_info(ticker: str) -> dict | None:
    def _fetch():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "country": info.get("country"),
            }
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)


async def get_previous_close(ticker: str) -> float | None:
    def _fetch():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                return round(hist["Close"].iloc[-2], 2)
            return None
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)


async def get_daily_pl_percent(ticker: str) -> float | None:
    current_price, prev_close = await asyncio.gather(
        get_stock_price(ticker),
        get_previous_close(ticker),
    )
    if current_price is None or prev_close is None or prev_close == 0:
        return None
    return round((current_price - prev_close) / prev_close * 100, 2)


async def get_daily_pl(ticker: str) -> float | None:
    current_price, prev_close = await asyncio.gather(
        get_stock_price(ticker),
        get_previous_close(ticker),
    )
    if current_price is None or prev_close is None:
        return None
    return round(current_price - prev_close, 2)

TRENDING_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "GOOGL", "META", "AMD", "PLTR", "NFLX"
]

NAMES = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corporation", "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla Inc.", "AMZN": "Amazon.com Inc.", "GOOGL": "Alphabet Inc.",
    "META": "Meta Platforms Inc.", "AMD": "Advanced Micro Devices",
    "PLTR": "Palantir Technologies", "NFLX": "Netflix Inc."
}

async def get_trending_stocks():
    async def _fetch_single(symbol: str):
        try:
            def _blocking():
                ticker = yf.Ticker(symbol)
                fast = ticker.fast_info
                last = fast.last_price
                prev = fast.previous_close
                return {
                    "ticker": symbol,
                    "name": NAMES.get(symbol, symbol),
                    "price": round(last, 2),
                    "priceChange": round(((last - prev) / prev) * 100, 2)
                }
            return await asyncio.to_thread(_blocking)
        except Exception:
            return None

    results = await asyncio.gather(*[_fetch_single(s) for s in TRENDING_SYMBOLS])
    results = [r for r in results if r is not None]

    return {"trending": results} if results else None

async def get_holding_stats(ticker: str) -> dict | None:
    def _fetch():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            prev = info.get("previousClose", 0)
            daily_pl = current - prev
            daily_pl_percent = ((current - prev) / prev) * 100 if prev > 0 else 0
            return {
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "price": round(current, 2),
                "daily_pl": round(daily_pl, 2),
                "daily_pl_percent": round(daily_pl_percent, 2),
            }
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)

async def get_specific_holding(ticker: str, user_id: int) -> dict |None:
    db = SessionLocal()
    try:
        current = await get_stock_price(ticker)
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        holding = db.query(Holding).filter(Holding.user_id == user_id, ticker == Holding.ticker).first()
        if holding is None:
            return None
        buy_in_total = float(holding.buy_in_price) * holding.quantity
        current_total = round(holding.quantity * current, 2)
        return {
            "quantity": holding.quantity,
            "currentPrice": current_total,
            "buyInPrice": round(buy_in_total, 2),
            "changeSinceBuy": round(((current_total/buy_in_total)-1)*100, 2)
        }
    finally:
        db.close()


async def get_stock_stats(ticker: str) -> dict | None:
    def _fetch():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            try:
                current_price = stock.fast_info.get("last_price", info.get("regularMarketPrice", 0))
            except Exception:
                current_price = info.get("regularMarketPrice", 0)

            previous_close = info.get("previousClose", 0)
            change_abs = current_price - previous_close if previous_close else 0
            change_percent = (change_abs / previous_close) * 100 if previous_close else 0

            hist = stock.history(period="2d")
            today = hist.iloc[-1] if not hist.empty else None
            day_high = today["High"] if today is not None else info.get("dayHigh", 0)
            day_low = today["Low"] if today is not None else info.get("dayLow", 0)

            return {
                "price": round(current_price, 2),
                "changePercent": round(change_percent, 2),
                "dayHigh": round(day_high, 2),
                "dayLow": round(day_low, 2),
                "fiftyTwoWeekHigh": round(info.get("fiftyTwoWeekHigh", 0), 2),
                "fiftyTwoWeekLow": round(info.get("fiftyTwoWeekLow", 0), 2),
                "volume": info.get("volume", 0),
                "marketCap": info.get("marketCap", 0),
                "dividendRate": info.get("dividendRate", 0),
            }
        except Exception:
            return None
    return await asyncio.to_thread(_fetch)