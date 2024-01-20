# pylint: disable=missing-module-docstring
from math import ceil
from operator import itemgetter
from src.application.barrels.schemas import Barrel
from src.application.inventory import inventory

MIN_STOCK_ML = 1000


def receive_delivery(barrels: list[Barrel]):
    """Add barrels to stock"""
    bought_items = [
        {"sku": item.sku, "quantity": item.quantity, "unit_price": item.price}
        for item in barrels
    ]

    ml_received = [0, 0, 0, 0]
    for barrel in barrels:
        for col, ml in enumerate(barrel.potion_type):
            ml_received[col] += ml * barrel.quantity
        inventory.update_sku_data(barrel.sku, barrel.price, barrel.potion_type)
    inventory.buy_from(bought_items, "BarrelSeller")
    inventory.add_ingredients_to_stock(ml_received)
    return "OK"


def choose_barrels_to_buy(wholesale_catalog: list[Barrel]):
    """Decide which barrels to buy"""
    gold_left = inventory.get_available_gold()
    stock_ml = inventory.get_available_stock_ml()

    plan = []
    colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]
    for barrel in sorted(wholesale_catalog, key=itemgetter("price")):
        qty_can_buy = gold_left // max(barrel.price, 0.0001)
        if qty_can_buy == 0:
            continue

        qty_should_buy = 0
        barrel_ml = dict(zip(colors, barrel.potion_type))
        for col, ml in barrel_ml.items():
            if ml > 0 and stock_ml[col] < MIN_STOCK_ML:
                qty_needed = ceil((MIN_STOCK_ML - stock_ml[col]) / ml)
                qty_should_buy = max(qty_should_buy, qty_needed)

        if qty_should_buy > 0:
            qty_to_buy = min(qty_should_buy, qty_can_buy, barrel.quantity)

            gold_left -= qty_to_buy * barrel.price
            for col, ml in barrel_ml.items():
                stock_ml[col] += ml * qty_to_buy

            plan.append({"sku": barrel.sku, "quantity": qty_to_buy})
    return plan
