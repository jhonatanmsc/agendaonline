import pdb
from datetime import timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.models import *
from app.pydantics import *
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.utils.auth import get_current_user, authenticate_user, create_token, verify_refresh_token
from app.utils.pagination import with_pagination

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/new-user")
async def new_user(user: UserInDB):
    db_user = Users.objects(email=user.email).first()
    if db_user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder({
                "errors": {
                    "email": ["Já existe um usuário com esse email"],
                }
            }),
        )
    if user.password != user.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As senhas não são iguais",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = user.dict()
    data.pop('password_confirmation')
    db_user = Users(**data).save()
    return db_user.as_dict()


@app.get('/me', response_model=UserRes)
async def me(current_user: Users = Depends(get_current_user)):
    return current_user.as_dict()


@app.put('/me', response_model=UserRes)
async def me(
    user: User,
    current_user: Users = Depends(get_current_user)
):
    current_user.update(**user.dict())
    return current_user.as_dict()


@app.put('/change-password', response_model=UserRes)
async def change_password(
    change_password_data: ChangePasswordData,
    current_user: Users = Depends(get_current_user)
):
    if not current_user.verify_password(change_password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if change_password_data.password != change_password_data.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As senhas não são iguais",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_user.set_password(change_password_data.password)
    return current_user.as_dict()


@app.post("/login", response_model=Token)
async def login(auth: AuthLogin):
    user = authenticate_user(auth.email, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email ou Senha errados",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raw_user = user.as_dict()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": raw_user['id']}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token(
        data={"sub": raw_user['id']}, expires_delta=refresh_token_expires
    )
    return {
        "user_data": raw_user,
        "token_type": "bearer",
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@app.post("/token/refresh", response_model=Token)
async def refresh(refresh_token: str):
    user = verify_refresh_token(refresh_token)
    raw_user = user.as_dict()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": raw_user['id']}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@app.get("/contacts", response_model=Pagination)
async def list_contacts(
    current: int = 1,
    page_size: int = 10,
    order_sorted: Optional[str] = None,
    field_sorted: Optional[str] = None,
    current_user: Users = Depends(get_current_user),
):
    params = {"current": current, "page_size": page_size}
    return with_pagination(Contacts, {}, params, order_sorted, field_sorted)


@app.post("/contacts", response_model=ContactRes)
async def new_contact(
    contact: Contact,
    current_user: Users = Depends(get_current_user),
):
    db_contact = Contacts.objects(name=contact.name, cellphone=contact.cellphone).first()
    if db_contact:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contato já existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_contact = Contacts(**contact.dict()).save()
    return db_contact.as_dict()


@app.get("/contacts/{contact_id}", response_model=ContactRes)
async def retrieve_contact(
    contact_id: str,
    current_user: Users = Depends(get_current_user),
):
    db_contact = Contacts.objects(id=contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_contact.as_dict()


@app.put("/contacts/{contact_id}", response_model=ContactRes)
async def update_contact(
    contact_id: str,
    contact: Contact,
    current_user: Users = Depends(get_current_user),
):
    db_contact = Contacts.objects(id=contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_contact.update(**contact.dict())
    return db_contact.as_dict()


@app.delete("/contacts/{contact_id}", response_model=ContactRes)
async def delete_contact(
    contact_id: str,
    current_user: Users = Depends(get_current_user),
):
    db_contact = Contacts.objects(id=contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_contact.delete()
    return db_contact.as_dict()


@app.get("/registries", response_model=Pagination)
async def list_registries(
    current: int = 1,
    page_size: int = 10,
    order_sorted: Optional[str] = None,
    field_sorted: Optional[str] = None,
    current_user: Users = Depends(get_current_user),
):
    query = {"is_active": True}
    params = {"current": current, "page_size": page_size}
    return with_pagination(Registries, query, params, order_sorted, field_sorted)


@app.post("/registries", response_model=RegistryRes)
async def new_registry(
    registry: Registry,
    current_user: Users = Depends(get_current_user),
):
    db_registry = Registries.objects(created_at=date.today(), category=registry.category).first()
    if db_registry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Já existe um registro para a mesma categoria no mesmo dia.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_registry = Registries(**registry.dict()).save()
    return db_registry.as_dict()


@app.get("/registries/{registry_id}", response_model=RegistryRes)
async def retrieve_registry(
    registry_id: str,
    current_user: Users = Depends(get_current_user),
):
    db_registry = Registries.objects(id=registry_id).first()
    if not db_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_registry.as_dict()


@app.put("/registries/{registry_id}", response_model=RegistryRes)
async def update_registry(
    registry_id: str,
    registry: Registry,
    current_user: Users = Depends(get_current_user),
):
    db_registry = Registries.objects(id=registry_id).first()
    if not db_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_registry.update(**registry.dict())
    return db_registry.as_dict()


@app.delete("/registries/{registry_id}", response_model=RegistryRes)
async def delete_registry(
    registry_id: str,
    current_user: Users = Depends(get_current_user),
):
    db_registry = Registries.objects(id=registry_id).first()
    if not db_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_registry.is_active = False
    db_registry.save()
    return db_registry.as_dict()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
