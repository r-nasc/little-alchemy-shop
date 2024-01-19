# pylint: disable=missing-module-docstring
from fastapi import APIRouter
from src.application.inventory import inventory

router = APIRouter()


@router.get("/gold", tags=["inventory"])
def get_gold():
    """Returns the current available gold"""
    return inventory.get_available_gold()


@router.get("/stock", tags=["inventory"])
def get_stock(item_sku: str = None, potions_only: bool = False):
    """Returns the stock of an SKU"""
    return inventory.get_available_stock(item_sku, potions_only)


@router.get("/stock_ml", tags=["inventory"])
def get_stock_ml():
    """Returns the stock of a color in mililiters"""
    return inventory.get_available_stock_ml()


@router.get("/cost_ml", tags=["inventory"])
def get_cost_ml():
    """Returns the cost of a color per mililiter"""
    return inventory.get_cost_per_ml()
