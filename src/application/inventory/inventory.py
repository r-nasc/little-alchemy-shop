# pylint: disable=missing-module-docstring, not-callable
from sqlalchemy import func
from src import database as db
from src.application.barrels.schemas import Barrel
from src.application.bottler.schemas import PotionInventory
from src.application.carts.schemas import ItemSkuDB
from src.application.inventory.schemas import (
    IngredientDB,
    IngredientLedgerDB,
    LedgerEntryDB,
    StockItem,
    TransactionDB,
)

__all__ = ["buy_from", "sell_to", "sell_to"]


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


def buy_from(items: list[dict], seller: str):
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


def sell_to(items: list[dict], buyer: str):
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


def update_sku_data(sku: str, price: float, colors: list[int]):
    """Update or insert SKU data on database"""
    with db.get_session() as sess:
        query = sess.query(ItemSkuDB).filter(ItemSkuDB.item_sku == sku)

        existing_sku = query.one_or_none()
        if existing_sku:
            if existing_sku.price == price:
                return
            with sess.begin():
                existing_sku.price = price
        else:
            with sess.begin():
                new_sku = ItemSkuDB(
                    item_sku=sku,
                    price=price,
                    red_ml=colors[0],
                    green_ml=colors[1],
                    blue_ml=colors[2],
                    dark_ml=colors[3],
                )
                sess.add(new_sku)


def get_available_gold() -> int:
    """Returns the available gold"""
    with db.get_session() as sess:
        query = sess.query(func.sum(LedgerEntryDB.gold_change))
        return query.scalar()


def get_available_stock(sku: str = None, potions_only=False) -> list[StockItem]:
    """Returns the available sku stock"""
    with db.get_session() as sess:
        query = sess.query(
            ItemSkuDB.item_sku.label("item_sku"),
            func.sum(func.coalesce(LedgerEntryDB.quantity_change, 0)).label("quantity"),
            ItemSkuDB.price.label("price"),
            ItemSkuDB.red_ml.label("red_ml"),
            ItemSkuDB.green_ml.label("green_ml"),
            ItemSkuDB.blue_ml.label("blue_ml"),
            ItemSkuDB.dark_ml.label("dark_ml"),
        ).join(ItemSkuDB, isouter=True, full=True)

        if sku:
            query = query.filter(ItemSkuDB.item_sku == sku)

        query = query.group_by(
            ItemSkuDB.item_sku, "price", "red_ml", "green_ml", "blue_ml", "dark_ml"
        )
        if potions_only:
            query = query.filter(ItemSkuDB.item_sku.icontains("POTION"))
        return [StockItem(**x._asdict()) for x in query.all()]


def get_available_stock_ml() -> dict[str, int]:
    """Returns the available ml of each type"""
    with db.get_session() as sess:
        red_ml = func.sum(IngredientLedgerDB.red_ml_change).label("red_ml")
        green_ml = func.sum(IngredientLedgerDB.green_ml_change).label("green_ml")
        blue_ml = func.sum(IngredientLedgerDB.blue_ml_change).label("blue_ml")
        dark_ml = func.sum(IngredientLedgerDB.dark_ml_change).label("dark_ml")

        return sess.query(red_ml, green_ml, blue_ml, dark_ml).one()._asdict()


def get_cost_per_ml() -> dict[str, int]:
    """Returns average cost per ml of each type"""
    with db.get_session() as sess:
        tbl = IngredientLedgerDB
        cols = {
            "red_ml": tbl.red_ml_change,
            "green_ml": tbl.green_ml_change,
            "blue_ml": tbl.blue_ml_change,
            "dark_ml": tbl.dark_ml_change,
        }

        cost = func.sum(tbl.gold_cost)
        costs_per_ml = {
            lbl: sess.query(func.sum(col) / cost).filter(col > 0).scalar()
            for lbl, col in cols.items()
        }
        return costs_per_ml


def add_ingredients_to_stock(barrels: list[Barrel]):
    """Add bought ingredients to stock"""
    with db.get_session() as sess, sess.begin():
        for barr in barrels:
            qty, pot_type = barr.quantity, barr.potion_type
            desc = f"Bought {qty}x [{pot_type}] for {barr.price}/pc"
            transaction = IngredientDB(description=desc)
            sess.add(transaction)

            ledger_entry = IngredientLedgerDB(
                transaction_id=transaction.id,
                gold_cost=barr.price * qty,
                red_ml_change=pot_type[0] * qty,
                green_ml_change=pot_type[1] * qty,
                blue_ml_change=pot_type[2] * qty,
                dark_ml_change=pot_type[3] * qty,
            )
            sess.add(ledger_entry)


def add_potions_sub_ingredients(potions: list[PotionInventory]):
    """Consume ingredients from stock and add potions"""
    with db.get_session() as sess, sess.begin():
        for pot in potions:
            qty, ing = pot.quantity, pot.potion_type
            tran1 = IngredientDB(
                description=f"Consumed {qty}x [{ing}] bottling potions"
            )
            sess.add(tran1)

            ledger_entry = IngredientLedgerDB(
                transaction_id=tran1.id,
                gold_cost=0,
                red_ml_change=ing[0] * qty,
                green_ml_change=ing[1] * qty,
                blue_ml_change=ing[2] * qty,
                dark_ml_change=ing[3] * qty,
            )
            sess.add(ledger_entry)

            tran2 = TransactionDB(description=f"Bottled {qty}x [{ing}] potions")
            sess.add(tran2)

            ledger_entry = LedgerEntryDB(
                transaction_id=tran2.id,
                item_sku=f"POTION_{ing[0]}_{ing[1]}_{ing[2]}_{ing[3]}",
                quantity_change=qty,
                gold_change=0,
            )
            sess.add(ledger_entry)


def reset_progress(sess: db.Session):
    """Reset shop progress"""
    sess.query(IngredientDB).delete()
    sess.query(IngredientLedgerDB).delete()
    sess.query(LedgerEntryDB).delete()
    sess.query(TransactionDB).delete()

    tran = TransactionDB(description="Received 100 starting gold")
    sess.add(tran)

    ledger_entry = LedgerEntryDB(
        transaction_id=tran.id,
        quantity_change=0,
        gold_change=100,
    )
    sess.add(ledger_entry)
