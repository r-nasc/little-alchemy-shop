# pylint: disable=missing-module-docstring
from logging import Logger
from fastapi import APIRouter, Depends

from src.api import auth
from src.application.bottler import bottler
from src.application.bottler.schemas import PotionInventory

logger = Logger(__name__)


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """Event fired when a potion is bottled"""
    logger.info("Bottles Received: %s", potions_delivered)
    return bottler.receive_delivery(potions_delivered)


# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """Event fired when a potions can be bottled"""
    bottling_list = bottler.choose_potions_to_bottle()
    logger.info("Bottling potions: %s", bottling_list)
    return bottling_list
