# pylint: disable=not-callable, missing-class-docstring, no-name-in-module, missing-module-docstring
import datetime as dt
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.application.schemas import BaseDB


class TransactionDB(BaseDB):
    __tablename__ = "transaction_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Transaction([{self.created_at}][{self.id}] {self.description})"


class LedgerEntryDB(BaseDB):
    __tablename__ = "transaction_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction_history.id"))
    item_sku: Mapped[str] = mapped_column(ForeignKey("item_sku.item_sku"))
    quantity_change: Mapped[int]
    gold_change: Mapped[int]

    def __repr__(self) -> str:
        details = f"{self.item_sku=} {self.quantity_change=} {self.gold_change=}"
        return f"Transaction([{self.id}] {self.transaction_id=} {details})"


class StockItem(BaseModel):
    item_sku: str
    quantity: int
    price: int
    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int


class IngredientDB(BaseDB):
    __tablename__ = "ingredient_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Ingredient([{self.created_at}][{self.id}] {self.description})"


class IngredientLedgerDB(BaseDB):
    __tablename__ = "ingredient_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("ingredient_history.id"))
    red_ml_change: Mapped[int]
    green_ml_change: Mapped[int]
    blue_ml_change: Mapped[int]
    dark_ml_change: Mapped[int]
    gold_cost: Mapped[int]

    def __repr__(self) -> str:
        details = (
            f"{self.red_ml_change=} {self.green_ml_change=}"
            f"{self.blue_ml_change=} {self.dark_ml_change=}"
        )
        return f"IngredientTransaction([{self.id}] {self.transaction_id=} {details})"
