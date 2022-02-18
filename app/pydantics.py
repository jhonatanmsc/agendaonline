from typing import Optional

from pydantic import BaseModel


class AuthLogin(BaseModel):
    email: str
    password: str


class TokenData(BaseModel):
    user_uid: Optional[str] = None


class RefreshTokenData(BaseModel):
    email: str


class User(BaseModel):
    name: str
    email: str
    category: str
    cellphone: str


class UserRes(User):
    id: str
    created_at: str


class Token(BaseModel):
    user_data: UserRes
    token_type: str
    access_token: str
    refresh_token: str


class UserInDB(User):
    password: str
    password_confirmation: str


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


class ChangePasswordData(BaseModel):
    current_password: str
    password: str
    password_confirmation: str
