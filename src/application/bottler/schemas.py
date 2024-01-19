# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring
from pydantic import BaseModel


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int
