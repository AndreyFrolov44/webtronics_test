import enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Boolean
)

from .base import metadata


# class ReactionsEnum(enum.Enum):
#     like = 'like'
#     dislike = 'dislike'


user = Table(
    "users",
    metadata,
    Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('username', String, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('password_hash', String, nullable=False),
)


post = Table(
    "posts",
    metadata,
    Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('title', String(100), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('content', Text, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
)

post_reaction = Table(
    "post_reactions",
    metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    # Column("reactions", Enum(ReactionsEnum), nullable=False)
    Column('is_like', Boolean, default=False, nullable=False),
    Column('is_dislike', Boolean, default=False, nullable=False)

)