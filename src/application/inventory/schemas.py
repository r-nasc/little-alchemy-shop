# pylint: disable=not-callable, missing-class-docstring, no-name-in-module
import datetime as dt
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.application.schemas import BaseDB, OrmBaseModel


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
