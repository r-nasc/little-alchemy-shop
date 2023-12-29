from fastapi import APIRouter, Depends

from src import database as db
from src.api import auth
from src.application.schemas import Barrel, InventoryDB

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """Event fired when a barrel is delivered"""
    print(barrels_delivered)

    delivered_red_ml = sum(
        x.ml_per_barrel * x.quantity
        for x in barrels_delivered
        if x.sku == "SMALL_RED_BARREL"
    )

    gold_cost = sum(x.price * x.quantity for x in barrels_delivered)

    with db.get_session() as sess, sess.begin():
        inv = sess.get(InventoryDB, 1)
        inv.num_red_ml = InventoryDB.num_red_potions + delivered_red_ml
        inv.gold = InventoryDB.gold - gold_cost

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Event fired when a barrel is available to be bought"""
    print(wholesale_catalog)

    with db.get_session() as sess:
        inv = sess.get(InventoryDB, 1)

    plan = []
    for barrel in wholesale_catalog:
        if (
            barrel.sku == "SMALL_RED_BARREL"
            and inv.gold >= barrel.price
            and inv.num_red_potions < 10
        ):
            buy_ord = {"sku": "SMALL_RED_BARREL", "quantity": 1}
            plan.append(buy_ord)
    return plan
