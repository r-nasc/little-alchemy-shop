# pylint: disable=missing-module-docstring
import os
from functools import lru_cache

import dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.application.schemas import BaseDB as Base

dotenv.load_dotenv()


@lru_cache
def get_engine() -> Engine:
    """Returns the DB engine"""
    db_url = os.environ.get("POSTGRES_URI")
    is_local = os.environ.get("IS_LOCAL") is not None
    return create_engine(db_url, pool_pre_ping=True, echo=is_local)


def get_session() -> Session:
    """Returns an ORM DB session"""
    return Session(get_engine())


engine = get_engine()
Base.metadata.create_all(engine)
