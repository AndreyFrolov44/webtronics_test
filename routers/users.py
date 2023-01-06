from fastapi import APIRouter

from models.users import UserIn, User
from services import users

router = APIRouter(tags=['user'])


@router.post("/", response_model=User)
async def register(
        userIn: UserIn,
):
    return await users.create(userIn)
