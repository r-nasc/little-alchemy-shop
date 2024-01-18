from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, synonym

# pylint: disable=missing-class-docstring, too-few-public-methods


class BaseDB(DeclarativeBase):
    pass


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True


class AuditResult(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool


class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int
