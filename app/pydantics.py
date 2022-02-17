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


class UserRes(User):
    id: str
    created_at: date


class UserInDB(User):
    password: str
    confirm_password: str


class Contact(BaseModel):
    name: str
    category: str
    cellphone: str


class ContactRes(Contact):
    id: str
    created_at: dict


class Registry(BaseModel):
    contacts: list
    category: str


class RegistryRes(Registry):
    id: str
    created_at: dict


class Pagination(BaseModel):
    data: list
    pagination: dict
