from datetime import datetime, timedelta, timezone
import jwt
from app.models import TokenData, User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import EmailStr
from sqlmodel import Session
from app.database import get_session
from app.config import settings as s

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, s.secret_key, algorithm=s.algorithm)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, s.secret_key, algorithms=[s.algorithm])
        id: str = payload.get("user_id")
        email: EmailStr = payload.get("username")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id = id, email = email)
    except InvalidTokenError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    token_data = verify_access_token(token, credentials_exception)
    user = session.get(User, token_data.id)
    if user is None:
        raise credentials_exception
    return user