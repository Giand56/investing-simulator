from fastapi import FastAPI

from src.database import engine, SessionLocal
from src.models.base import Base
from src.models.user import User
import src.models.user
import src.models.holding
from src.routers import stocks, portfolio
from src.schemas.test_schemas import TestUser

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(stocks.router)
app.include_router(portfolio.router)

#test:








