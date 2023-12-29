import math

from fastapi import APIRouter, Depends

from src import database as db
from src.api import auth
from src.application.schemas import PotionInventory, InventoryDB

ML_PER_BOTTLE = 100

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """Event fired after a potion is bottled"""
    print(potions_delivered)

    return "OK"


# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """Event fired when a potion can be bottled"""

    with db.get_session() as sess:
        inv = sess.get(InventoryDB, 1)

    return [
        {
            "potion_type": [100, 0, 0, 0],
            "quantity": math.floor(inv.num_red_ml / ML_PER_BOTTLE),
        }
    ]
