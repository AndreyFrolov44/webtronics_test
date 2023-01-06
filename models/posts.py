import datetime
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str


class PostDetail(PostBase):
    id: Optional[int]
    content: str
    date: datetime.datetime
    user_id: int
    like: int
    dislike: int


class Post(PostBase):
    id: int
    date: datetime.datetime
    like: int
    dislike: int
    user_id: int


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class PostCreate(PostBase):
    content: str


class PostReactions(BaseModel):
    post_id: int
    user_id: int
    is_like: bool
    is_dislike: bool
