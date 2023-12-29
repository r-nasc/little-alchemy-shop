from fastapi import APIRouter, Depends
from src.api import auth
from src import database as db
from src.application.schemas import AuditResult, InventoryDB

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/inventory")
def get_inventory():
    """Provides the current inventory"""
    with db.get_session() as sess:
        inv = sess.get(InventoryDB, 1)

    return {
        "number_of_potions": inv.num_red_potions,
        "ml_in_barrels": inv.num_red_ml,
        "gold": inv.gold,
    }


@router.post("/results")
def post_audit_results(audit_explanation: AuditResult):
    """Receives an audit result saying if the local inventory matches the remote one"""
    print(audit_explanation)

    return "OK"
