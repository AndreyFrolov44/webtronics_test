from fastapi import APIRouter, Depends, HTTPException, status

from models.posts import PostCreate, Post, PostDetail, PostUpdate
from models.users import User
from routers.depends import get_current_user
from services import posts

router = APIRouter(tags=['post'])


@router.post("/create", response_model=PostDetail)
async def create(
        create_post: PostCreate,
        current_user: User = Depends(get_current_user)
):
    """
    Создание нового поста
    """
    return await posts.create(post=create_post, user=current_user)


@router.get("/{post_id}", response_model=PostDetail)
async def post_detail(
        post_id: int,
):
    """
    Получить все содержимое поста
    """
    post = await posts.get_by_id(id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
    return post


@router.patch('/{post_id}', response_model=PostDetail)
async def post_update(
        post_id: int,
        post: PostUpdate,
        current_user: User = Depends(get_current_user)
):
    """
    Обновить содержимое поста
    """
    return await posts.update(post=post, post_id=post_id, user=current_user)


@router.delete('/{post_id}')
async def post_delete(
        post_id: int,
        current_user: User = Depends(get_current_user)
):
    """
    Удалить пост
    """
    return await posts.delete(post_id=post_id, user=current_user)


@router.post("/{post_id}/like", response_model=PostDetail)
async def like(
        post_id: int,
        current_user: User = Depends(get_current_user)
):
    """
    Поставить лайк посту
    """
    return await posts.like(post_id=post_id, user=current_user)


@router.post("/{post_id}/dislike", response_model=PostDetail)
async def dislike(
        post_id: int,
        current_user: User = Depends(get_current_user)
):
    """
    Поставить дизлайк посту
    """
    return await posts.dislike(post_id=post_id, user=current_user)


@router.get("/", response_model=list[Post])
async def read(
        user_id: int = None,
        limit: int = 100,
        offset: int = 0,
):
    """
    Получение всех постов
    """
    return await posts.get_all(user_id=user_id, limit=limit, offset=offset)
