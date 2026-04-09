import asyncio
import yfinance as yf

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