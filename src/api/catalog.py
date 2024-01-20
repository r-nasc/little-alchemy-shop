# pylint: disable=missing-module-docstring
from fastapi import APIRouter
from src.application.inventory import inventory

router = APIRouter()

MAX_CATALOG_ITEMS = 6


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """Returns a catalog of available potions"""
    return [
        {
            "sku": pot.item_sku,
            "name": pot.item_sku,
            "quantity": pot.quantity,
            "price": pot.price,
            "potion_type": [pot.red_ml, pot.green_ml, pot.blue_ml, pot.dark_ml],
        }
        for pot in inventory.get_available_stock(potions_only=True)
        if pot.quantity > 0
    ][:MAX_CATALOG_ITEMS]
