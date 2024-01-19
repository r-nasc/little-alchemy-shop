# pylint: disable=missing-class-docstring, too-few-public-methods, no-name-in-module, missing-module-docstring
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


class BaseDB(DeclarativeBase):
    pass


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True


class AuditResult(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool
