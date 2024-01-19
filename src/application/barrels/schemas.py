# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring
from pydantic import BaseModel


class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int
