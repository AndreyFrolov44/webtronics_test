from typing import Optional
from fastapi import HTTPException, status

from db.base import database
from models.users import User, UserIn, UserCreate
from db import user
from core.security import get_password_hash


async def get_by_username(username: str) -> Optional[UserCreate]:
    query = user.select().where(user.c.username == username)
    usr = await database.fetch_one(query)
    if usr is None:
        return None
    return UserCreate.parse_obj(usr)


async def create(usr: UserIn) -> Optional[User]:
    username_exist = await get_by_username(usr.username)
    if username_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Данный username уже используется")
    if usr.password != usr.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают")
    create_user = UserCreate(
        username=usr.username,
        email=usr.email,
        password_hash=get_password_hash(usr.password)
    )
    values = {**create_user.dict()}
    values.pop("id", None)
    query = user.insert().values(**values)
    create_user.id = await database.execute(query)
    return User(**create_user.dict())