from fastapi.security import OAuth2PasswordBearer
from mongoengine import *
from decouple import config as env
from passlib.context import CryptContext

DATABASE_URI = env("DATABASE_URI")
connect(host=DATABASE_URI)

SECRET_KEY = env('SECRET_KEY')
ALGORITHM = env('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = env('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)
REFRESH_TOKEN_EXPIRE_MINUTES = env('REFRESH_TOKEN_EXPIRE_MINUTES', cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

