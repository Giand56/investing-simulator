from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.auth import LoginResponse, LoginRequest, RegisterResponse, RegisterRequest
from src.services.auth_service import login_service, register_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_service(form_data.username, form_data.password)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    return register_service(request)

