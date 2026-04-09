from datetime import datetime, timedelta
import os
from fastapi import HTTPException


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from src.database import SessionLocal
from src.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM =  os.getenv('JWT_ALGORITHM')
EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_token(user_id: int) -> str:
    expiry = datetime.utcnow() + timedelta(minutes=EXPIRY_MINUTES)
    payload = {"sub": str(user_id), "exp": expiry}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(user_id)
    except:
        raise HTTPException(status_code = 401, detail = "Invalid token")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail = "User not found")
        return user
    finally:
        db.close()