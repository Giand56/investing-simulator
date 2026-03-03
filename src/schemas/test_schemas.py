from pydantic import BaseModel


class TestUser(BaseModel):
    cash_balance: float
    username: str