from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, Token
from app.utils import verify_password
from app.oauth2 import create_access_token
from app.config import settings as s

router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login", response_model=Token)
def login(*, user_creds: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    
    user = session.exec(select(User).where(User.email == user_creds.username)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Incorrect username or password")
    if not verify_password(user_creds.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Incorrect username or password")
    
    access_token_expires = timedelta(minutes=s.access_token_expire_minutes)
    access_token = create_access_token(
        data = {"user_id": user.id, "username": user.email},
        expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
