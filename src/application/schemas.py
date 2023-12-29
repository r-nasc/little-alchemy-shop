from enum import Enum
import datetime as dt
from pydantic import BaseModel, Json
from sqlalchemy import DateTime, func  # pylint: disable=no-name-in-module
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_json import NestedMutableJson

# pylint: disable=missing-class-docstring, too-few-public-methods


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


class NewCart(BaseModel):
    customer: str


class CartDbEntry(BaseModel):
    item_sku: str
    quantity: int


class Cart(BaseModel):
    cart_id: int
    customer: str
    contents: Json[dict[str, CartDbEntry]]
    updated_at: dt.datetime


class CartItem(BaseModel):
    quantity: int


class CartCheckout(BaseModel):
    payment: str


class SearchSortOptions(str, Enum):
    CUSTOMER_NAME = "customer_name"
    ITEM_SKU = "item_sku"
    LINE_ITEM_TOTAL = "line_item_total"
    TIMESTAMP = "timestamp"


class SearchSortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class BaseDB(DeclarativeBase):
    pass


class InventoryDB(BaseDB):
    __tablename__ = "global_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    num_red_potions: Mapped[int]
    num_red_ml: Mapped[int]
    gold: Mapped[int]

    def __repr__(self) -> str:
        return f"Inventory({self.num_red_potions=!r}, {self.num_red_ml=!r}, {self.gold=!r})"


class CartDB(BaseDB):
    __tablename__ = "cart"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    contents: Mapped[dict[str, CartDbEntry]] = mapped_column(NestedMutableJson)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"Cart({self.cart_id=!r}, {self.customer=!r}, {self.contents=!r})"
