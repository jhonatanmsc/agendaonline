import pdb
from datetime import date, timedelta, datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from app.models import Users
from app.pydantics import TokenData, User
from app.settings import oauth2_scheme, SECRET_KEY, ALGORITHM


def convert_datetime(dt: date) -> str:
    return dt.strftime('%Y-%m-%d')


def authenticate_user(email: str, password: str):
    user = Users.objects(email=email).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user.as_dict()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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
    user = Users.objects(id=token_data.user_uid).first()
    if user is None:
        raise credentials_exception
    return user.as_dict()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
