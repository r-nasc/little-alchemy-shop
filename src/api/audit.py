from fastapi import APIRouter, Depends
from src.api import auth
from src.application.inventory import inventory
from src.application.schemas import AuditResult

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/inventory")
def get_inventory():
    """Provides the current inventory"""
    barrels = inventory.get_available_stock_ml()
    potions = inventory.get_available_stock(potions_only=True)

    return {
        "number_of_potions": sum(pot.quantity for pot in potions),
        "ml_in_barrels": sum(barrels.values()),
        "gold": inventory.get_available_gold(),
    }


@router.post("/results")
def post_audit_results(audit_explanation: AuditResult):
    """Receives an audit result saying if the local inventory matches the remote one"""
    print(audit_explanation)

    return "OK"
