from fastapi import APIRouter

from . import auth, users, posts

router = APIRouter()
router.include_router(posts.router, prefix='/post')
router.include_router(auth.router, prefix='/login')
router.include_router(users.router, prefix='/user')

