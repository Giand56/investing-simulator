import yfinance as yf

def get_stock_price(ticker: str) -> float | None:
    stock = yf.Ticker(ticker)
    price = stock.fast_info["last_price"]
    return round(price, 2)

