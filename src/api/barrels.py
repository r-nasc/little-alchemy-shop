from math import ceil
from operator import itemgetter
from fastapi import APIRouter, Depends

from src import database as db
from src.api import auth
from src.application.inventory import inventory
from src.application.schemas import Barrel

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

MIN_STOCK_ML = 1000


@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """Event fired when a barrel is delivered"""
    print(barrels_delivered)

    bought_items = [
        {"sku": item.sku, "quantity": item.quantity, "unit_price": item.price}
        for item in barrels_delivered
    ]

    inventory.buy_batch_from(bought_items, "BarrelSeller")
    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Event fired when a barrel is available to be bought"""
    print(wholesale_catalog)

    gold_left = inventory.get_available_gold()
    stock_ml = inventory.get_available_stock_ml()

    plan = []
    colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]
    for barrel in sorted(wholesale_catalog, key=itemgetter("price")):
        qty_can_buy = gold_left // barrel.price
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
