from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI

from src.database import engine, SessionLocal
from src.models.base import Base
from src.models.user import User
import src.models.user
import src.models.holding
from src.routers import stocks, portfolio, auth
from src.schemas.test_schemas import TestUser
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(auth.router)







