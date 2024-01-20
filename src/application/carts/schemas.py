# pylint: disable=not-callable, missing-class-docstring, no-name-in-module, missing-module-docstring
from enum import Enum
import datetime as dt
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from src.application.schemas import BaseDB, OrmBaseModel


class NewCart(BaseModel):
    customer: str


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


class ItemSkuDB(BaseDB):
    __tablename__ = "item_sku"

    item_sku: Mapped[str] = mapped_column(primary_key=True)
    red_ml: Mapped[int]
    green_ml: Mapped[int]
    blue_ml: Mapped[int]
    dark_ml: Mapped[int]
    price: Mapped[int]

    def __repr__(self) -> str:
        col = f"{self.red_ml}, {self.red_ml}, {self.red_ml}, {self.dark_ml}"
        return f"ItemSku({self.item_sku}, col=({col}), price={self.price})"


class CartContentDB(BaseDB):
    __tablename__ = "cart_content"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.cart_id"))
    item_sku: Mapped[str] = mapped_column(ForeignKey("item_sku.item_sku"))
    line_item_total: Mapped[int]

    timestamp = synonym("updated_at")
    sku_data: Mapped[ItemSkuDB] = relationship("ItemSkuDB")

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(), server_default=func.now(), server_onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"CartContent({self.cart_id=!r}, {self.item_sku=!r}, {self.line_item_total=!r})"


class CartDB(BaseDB):
    __tablename__ = "cart"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str]
    contents: Mapped[list[CartContentDB]] = relationship("CartContentDB")

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Cart({self.cart_id=!r}, {self.customer_name=!r}, {self.contents=!r})"


class SearchResponseEntry(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: int
    timestamp: dt.datetime


class SearchResponse(BaseModel):
    previous: str
    next: str
    results: list[SearchResponseEntry]


class CartContent(OrmBaseModel):
    id: int
    cart_id: int
    item_sku: str
    line_item_total: int
    created_at: dt.datetime
    updated_at: dt.datetime


class Cart(OrmBaseModel):
    cart_id: int
    customer_name: str
    contents: list[CartContent]
    created_at: dt.datetime
