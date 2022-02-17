from datetime import timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends

from app.models import *
from app.pydantics import *
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils import authenticate_user, create_access_token, get_current_user, with_pagination

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/new-user", response_model=UserRes)
async def new_user(user: UserInDB):
    db_user = Users.objects(email=user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Já existe um usuário com esse email",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As senhas não são iguais",
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
    return {
        "user_data": user,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/contacts", response_model=Pagination)
async def list_contacts(
    current: int = 1,
    page_size: int = 10,
    order_sorted: Optional[str] = None,
    field_sorted: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    params = {"current": current, "page_size": page_size}
    return with_pagination(Contacts, {}, params, order_sorted, field_sorted)


@app.post("/contacts", response_model=ContactRes)
async def new_contact(
    contact: Contact,
    current_user: User = Depends(get_current_user),
):
    db_contact = Contacts.objects(name=contact.name, cellphone=contact.cellphone).first()
    if db_contact:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contato já existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_contact = Contacts(**contact.dict()).save()
    return db_contact.as_dict()


@app.get("/contacts/{contact_id}", response_model=ContactRes)
async def retrieve_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    query = {"is_active": True}
    params = {"current": current, "page_size": page_size}
    return with_pagination(Registries, query, params, order_sorted, field_sorted)


@app.post("/registries", response_model=RegistryRes)
async def new_registry(
    registry: Registry,
    current_user: User = Depends(get_current_user),
):
    db_registry = Registries.objects(created_at=date.today(), category=registry.category).first()
    if db_registry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Já existe um registro para a mesma categoria no mesmo dia.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_registry = Registries(**registry.dict()).save()
    return db_registry.as_dict()


@app.get("/registries/{registry_id}", response_model=RegistryRes)
async def retrieve_registry(
    registry_id: str,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
