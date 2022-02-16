import pdb
from datetime import date, timedelta, datetime
from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from uvicorn.main import logger

from app.models import Users
from app.pydantics import TokenData, User
from app.settings import oauth2_scheme, SECRET_KEY, ALGORITHM


def convert_datetime(dt: date) -> str:
    return dt.strftime('%Y-%m-%d')


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
    return user.as_dict()


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


def with_pagination(collection, query={}, args={}, order_sorted=None, field_sorted=None):
    """
        :param collection: Model
        :param query: filtro a ser aplicado
        :param args: esperado um dicionario com current e pageSize
        :param order_sorted: DESC ou ASC
        :param field_sorted: campo a ser ordenado
        :return: lista com paginação
        """
    offset = 1
    limit = 100
    if args.get('current') and args.get('page_size'):
        offset = int(args['current'])
        limit = int(args['page_size'])
    skips = limit * (offset - 1)
    res = {"pagination": {}}
    documents = collection.objects(__raw__=query)
    total = len(documents)
    if field_sorted and order_sorted:
        short = {'DESC': '-', 'ASC': '+'}
        order_by = f"{short[order_sorted]}{field_sorted}"
        documents = documents.order_by(order_by)
    data = documents.skip(skips).limit(limit)
    data = [item.as_dict() for item in data]
    max_page = int(total / limit) if total % limit == 0 else int(total / limit) + 1
    res["pagination"]["total"] = total
    res["pagination"]["max_page"] = max_page
    res["pagination"]["page_size"] = limit
    res["pagination"]["current"] = offset
    res["data"] = data
    return res
