import datetime
from typing import Optional
from sqlalchemy import text
from fastapi import HTTPException, status

from db.base import database
from models.posts import Post, PostCreate, PostDetail, PostReactions, PostUpdate
from models.users import User
from db import tables


async def get_all(user_id: Optional[int], limit: int = 100, offset: int = 0) -> list[Post]:
    if not user_id:
        query = text(f"""
            SELECT posts.*, COUNT(post_reactions.is_like) FILTER (WHERE post_reactions.is_like) as like, COUNT(post_reactions.is_dislike) FILTER (WHERE post_reactions.is_dislike) as dislike
            FROM posts
            FULL JOIN post_reactions ON posts.id = post_reactions.post_id
            GROUP BY posts.id, post_reactions.post_id
            LIMIT {limit} OFFSET {offset};
        """)
    else:
        query = text(f"""
            SELECT posts.*, COUNT(post_reactions.is_like) FILTER (WHERE post_reactions.is_like) as like, COUNT(post_reactions.is_dislike) FILTER (WHERE post_reactions.is_dislike) as dislike
            FROM posts
            FULL JOIN post_reactions ON posts.id = post_reactions.post_id
            WHERE posts.user_id = {user_id}
            GROUP BY posts.id, post_reactions.post_id
            LIMIT {limit} OFFSET {offset};
        """)
    return await database.fetch_all(query)


async def get_by_id(id: int) -> Optional[PostDetail]:
    query = text(f"""
        SELECT posts.*, COUNT(post_reactions.is_like) FILTER (WHERE post_reactions.is_like) as like, COUNT(post_reactions.is_dislike) FILTER (WHERE post_reactions.is_dislike) as dislike
        FROM posts
        FULL JOIN post_reactions ON posts.id = post_reactions.post_id
        WHERE posts.id = {id}
        GROUP BY posts.id, post_reactions.post_id
    """)
    p = await database.fetch_one(query)
    if p is None:
        return None
    return PostDetail.parse_obj(p)


async def get_reactions(post_id: int, user_id: int) -> Optional[PostReactions]:
    query = tables.post_reaction.select().where(tables.post_reaction.c.user_id == user_id, tables.post_reaction.c.post_id == post_id)
    pr = await database.fetch_one(query)
    if pr is None:
        return None
    return PostReactions.parse_obj(pr)


async def like(post_id: int, user: User) -> PostDetail:
    post = await get_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
    if post.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы не можете оценивать свои посты')
    reactions = await get_reactions(post_id, user.id)
    if reactions is not None and (not reactions.is_like or not reactions.is_dislike):
        if reactions.is_like:
            reactions.is_like = False
        elif reactions.is_dislike:
            reactions.is_dislike = False
            reactions.is_like = True
        else:
            reactions.is_like = True
        return await update_reactions(post_id, user.id, reactions)
    else:
        reactions = PostReactions(
            post_id=post_id,
            user_id=user.id,
            is_like=True,
            is_dislike=False,
        )

    values = {**reactions.dict()}
    query = tables.post_reaction.insert().values(**values)
    await database.execute(query)
    return await get_by_id(post_id)


async def dislike(post_id: int, user: User) -> PostDetail:
    post = await get_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
    if post.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы не можете оценивать свои посты')
    reactions = await get_reactions(post_id, user.id)
    if reactions is not None and (not reactions.is_like or not reactions.is_dislike):
        if reactions.is_like:
            reactions.is_dislike = True
            reactions.is_like = False
        elif reactions.is_dislike:
            reactions.is_dislike = False
        else:
            reactions.is_dislike = True
        return await update_reactions(post_id, user.id, reactions)
    else:
        reactions = PostReactions(
            post_id=post_id,
            user_id=user.id,
            is_like=False,
            is_dislike=True,
        )

    values = {**reactions.dict()}
    query = tables.post_reaction.insert().values(**values)
    await database.execute(query)
    return await get_by_id(post_id)


async def update_reactions(post_id: int, user_id:int, reaction: PostReactions) -> PostDetail:
    values = {**reaction.dict()}
    query = tables.post_reaction.update().where(tables.post_reaction.c.user_id == user_id, tables.post_reaction.c.post_id == post_id).values(**values)
    await database.execute(query)
    return await get_by_id(post_id)


async def create(post: PostCreate, user: User) -> Optional[PostDetail]:
    create_post = PostDetail(
        title=post.title,
        date=datetime.datetime.now(),
        content=post.content,
        user_id=user.id,
        like=0,
        dislike=0
    )
    values = {**create_post.dict()}
    values.pop('id', None)
    values.pop('like', None)
    values.pop('dislike', None)
    query = tables.post.insert().values(**values)
    create_post.id = await database.execute(query)
    return PostDetail(**create_post.dict())


async def update(post: PostUpdate, post_id: int, user: User) -> PostDetail:
    current_post = await get_by_id(post_id)
    if current_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
    if current_post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет доступа к данному посту')
    values = {**post.dict()}
    values = {k: v for k, v in values.items() if v}
    query = tables.post.update().where(tables.post.c.id == post_id).values(**values)
    await database.execute(query)
    return await get_by_id(post_id)


async def delete(post_id: int, user: User):
    post = await get_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет доступа к данному посту')
    query = tables.post.delete().where(tables.post.c.id == post_id)
    await database.execute(query)
