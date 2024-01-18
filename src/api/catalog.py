from fastapi import APIRouter
from src import database as db
from src.application.inventory import inventory

router = APIRouter()


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
    ]


@router.get("/gold", tags=["catalog"])
def get_gold():
    """Returns the current available gold"""
    return inventory.get_available_gold()


@router.get("/stock", tags=["catalog"])
def get_stock(item_sku: str = None, potions_only: bool = False):
    """Returns the stock of an SKU"""
    return inventory.get_available_stock(item_sku, potions_only)


@router.get("/stock_ml", tags=["catalog"])
def get_stock_ml():
    """Returns the stock of a color in mililiters"""
    res = inventory.get_available_stock_ml()
    return res
