from fastapi import APIRouter, Depends

from src.api import auth
from src.application.admin import admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    return admin.reset_progress()


@router.get("/shop_info/")
def get_shop_info():
    """Returns shop info"""
    return {
        "shop_name": "LittleAlchemyShop",
        "shop_owner": "r-nasc",
    }
