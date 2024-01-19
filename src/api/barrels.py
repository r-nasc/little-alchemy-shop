# pylint: disable=missing-module-docstring
from logging import Logger
from fastapi import APIRouter, Depends

from src.api import auth
from src.application.barrels import barrels
from src.application.barrels.schemas import Barrel

logger = Logger(__name__)

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """Event fired when a barrel is delivered"""
    logger.info("Barrels Received: %s", barrels_delivered)
    return barrels.receive_delivery(barrels_delivered)


@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Event fired when a barrel is available to be bought"""
    logger.info("Barrels can be bought: %s", wholesale_catalog)
    shopping_list = barrels.choose_barrels_to_buy(wholesale_catalog)
    logger.info("Ordering Barrels: %s", shopping_list)
    return shopping_list
