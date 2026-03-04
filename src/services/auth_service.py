from fastapi import HTTPException

from src.auth import verify_password, create_token, hash_password
from src.database import SessionLocal
from src.models.user import User
from src.schemas.auth import LoginRequest, RegisterRequest

default_cash_balance = 10000


def login_service(username: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is not None:
            if verify_password(password, user.password):
                token = create_token(user.id)
                return {"access_token": token, "token_type": "bearer"}
            else:
                raise HTTPException(status_code=401, detail="Incorrect username or password")
        else:
            raise HTTPException(status_code=401, detail="User does not exist")
    finally:
        db.close()

def register_service(request: RegisterRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == request.username).first()
        if user is None:
            new_user = User(cash_balance = default_cash_balance,
                            username = request.username,
                            password = hash_password(request.password))
            db.add(new_user)
            db.commit()
            token = create_token(new_user.id)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="User already exists")
    finally:
        db.close()