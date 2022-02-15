from datetime import date
from typing import Optional

from pydantic import BaseModel


class AuthLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_uid: Optional[str] = None


class User(BaseModel):
    name: str
    email: str
    category: str
    cellphone: str


class UserInDB(User):
    password: str


class Contact(BaseModel):
    name: str
    category: str
    cellphone: str


class Registry(BaseModel):
    created_at = date
    contacts = list[Contact]
    category = str
