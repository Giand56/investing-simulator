from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///investing.db")

SessionLocal = sessionmaker(bind=engine)