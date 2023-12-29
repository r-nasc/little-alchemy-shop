from fastapi import APIRouter
from src import database as db
from src.application.schemas import InventoryDB

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.get_session() as sess:
        inv = sess.get(InventoryDB, 1)
        red_count = inv.num_red_potions

    return [
        {
            "sku": "RED_POTION_0",
            "name": "red potion",
            "quantity": red_count,
            "price": 50,
            "potion_type": [100, 0, 0, 0],
        }
    ]
