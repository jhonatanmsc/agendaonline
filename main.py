import pdb
from datetime import timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends

from app.models import *
from app.pydantics import *
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils import authenticate_user, create_access_token, get_current_user

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/registry", response_model=User)
async def registry(user: UserInDB):
    db_user = Users.objects(email=user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Já existe um usuário com esse email",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_user = Users(**user.dict()).save()
    return db_user.as_dict()


@app.post("/login", response_model=Token)
async def login(auth: AuthLogin):
    user = authenticate_user(auth.email, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou Senha errados",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['id']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
