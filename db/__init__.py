from .tables import user, post, post_reaction
from .base import metadata, engine


def init_db():
    metadata.create_all(engine)
