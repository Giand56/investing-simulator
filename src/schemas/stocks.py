from typing import List

from pydantic import BaseModel

class ShortInfo(BaseModel):
    ticker: str
    name: str
    price: float
    priceChange: float

class Trending(BaseModel):
    trending: List[ShortInfo]