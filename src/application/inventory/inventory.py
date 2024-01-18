from typing import Union
from sqlalchemy import func
from src import database as db
from src.application.carts.schemas import ItemSkuDB
from src.application.inventory.schemas import LedgerEntryDB, StockItem, TransactionDB

__all__ = ["buy_from", "sell_to", "sell_batch_to"]

# pylint: disable=not-callable


def register_transactions(items: list[dict]):
    """Creates a new transaction and add it to the ledger"""
    with db.get_session() as sess, sess.begin():
        for item in items:
            transaction = TransactionDB(description=item["desc"])
            sess.add(transaction)
            ledger_entry = LedgerEntryDB(
                transaction_id=transaction.id,
                item_sku=item["sku"],
                quantity_change=item["quantity_change"],
                gold_change=item["gold_change"],
            )
            sess.add(ledger_entry)


def buy_from(sku: str, quantity: int, unit_price: int, seller: str):
    """Register a new transaction on the ledger"""
    item = {"sku": sku, "quantity": quantity, "unit_price": unit_price}
    buy_batch_from([item], seller)


def sell_to(sku: str, quantity: int, unit_price: int, buyer: str):
    """Register a new transaction on the ledger"""
    item = {"sku": sku, "quantity": quantity, "unit_price": unit_price}
    sell_batch_to([item], buyer)


def buy_batch_from(items: list[dict], seller: str):
    """Register a batch of new transactions on the ledger"""
    transactions = []
    for item in items:
        qty, price = item["quantity"], item["unit_price"]
        sku, cost = item["sku"], price * qty
        new_tran = {
            "desc": f"Bought {qty}x {sku} from {seller} for {price}/pc [Total: {cost}]",
            "sku": sku,
            "quantity_change": qty,
            "gold_change": cost * -1,
        }
        transactions.append(new_tran)
    register_transactions(transactions)


def sell_batch_to(items: list[dict], buyer: str):
    """Register a batch of new transactions on the ledger"""
    transactions = []
    for item in items:
        qty, price = item["quantity"], item["unit_price"]
        sku, profit = item["sku"], price * qty
        new_tran = {
            "desc": f"Sold {qty}x {sku} to {buyer} for {price}/pc [Total: {profit}]",
            "sku": sku,
            "quantity_change": qty * -1,
            "gold_change": profit,
        }
        transactions.append(new_tran)
    register_transactions(transactions)


def get_available_gold() -> int:
    """Returns the available gold"""
    with db.get_session() as sess:
        query = sess.query(func.sum(LedgerEntryDB.gold_change))
        return query.scalar()


def get_available_stock(sku: str = None, potions_only=False) -> list[StockItem]:
    """Returns the available sku stock"""
    with db.get_session() as sess:
        query = sess.query(
            LedgerEntryDB.item_sku.label("item_sku"),
            func.sum(LedgerEntryDB.quantity_change).label("quantity"),
            ItemSkuDB.price.label("price"),
            ItemSkuDB.red_ml.label("red_ml"),
            ItemSkuDB.green_ml.label("green_ml"),
            ItemSkuDB.blue_ml.label("blue_ml"),
            ItemSkuDB.dark_ml.label("dark_ml"),
        ).join(ItemSkuDB)

        if sku:
            query = query.filter(LedgerEntryDB.item_sku == sku)

        query = query.group_by(
            LedgerEntryDB.item_sku, "price", "red_ml", "green_ml", "blue_ml", "dark_ml"
        )
        if potions_only:
            query = query.filter(LedgerEntryDB.item_sku.icontains("POTION"))
        return [StockItem(**x._asdict()) for x in query.all()]


def get_available_stock_ml() -> Union[int, dict[str, int]]:
    """Returns the available ml of each type"""
    with db.get_session() as sess:
        qty = LedgerEntryDB.quantity_change
        red_ml = func.sum(qty * ItemSkuDB.red_ml).label("red_ml")
        green_ml = func.sum(qty * ItemSkuDB.green_ml).label("green_ml")
        blue_ml = func.sum(qty * ItemSkuDB.blue_ml).label("blue_ml")
        dark_ml = func.sum(qty * ItemSkuDB.dark_ml).label("dark_ml")

        query = sess.query(red_ml, green_ml, blue_ml, dark_ml).join(ItemSkuDB)
        query = query.filter(LedgerEntryDB.item_sku.icontains("BARREL"))
        return query.one()._asdict()
