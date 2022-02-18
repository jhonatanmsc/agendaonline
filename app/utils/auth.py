import pytz
from datetime import date, timedelta, datetime
from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from uvicorn.main import logger

from app.models import Users
from app.pydantics import TokenData, User, RefreshTokenData
from app.settings import oauth2_scheme, SECRET_KEY, ALGORITHM


# def auth_required(func):
#     @wraps(func)
#     async def wrapper(auth, *args, **kwargs):
#         return await func(auth, *args, **kwargs)
#     return wrapper


def authenticate_user(email: str, password: str):
    user = Users.objects(email=email, is_active=True).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uid: str = payload.get("sub")
        if user_uid is None:
            raise credentials_exception
        token_data = TokenData(user_uid=user_uid)
    except JWTError:
        raise credentials_exception
    user = Users.objects(id=token_data.user_uid, is_active=True).first()
    if user is None:
        raise credentials_exception
    return user


def verify_refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        exp: int = payload.get("exp")
        now = datetime.utcnow()
        exp_date = datetime.utcfromtimestamp(exp)
        if now > exp_date:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="RefreshToken inválido.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = RefreshTokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = Users.objects(id=token_data.email, is_active=True).first()
    if user is None:
        raise credentials_exception
    return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
