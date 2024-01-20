from logging import Logger

from fastapi import HTTPException
from sqlalchemy import desc

from src import database as db
from src.application.carts.schemas import (
    Cart,
    CartContentDB,
    CartDB,
    ItemSkuDB,
    SearchResponse,
)
from src.application.inventory import inventory

logger = Logger(__name__)


def get_by_id(cart_id: int) -> Cart:
    """Returns an existing cart or raises"""
    with db.get_session() as sess:
        cart: Cart = sess.get(CartDB, cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="CartNotFound")
        return cart


def get_contents_by_id(cart_id: int) -> list[CartContentDB]:
    """Returns contents of an existing cart"""
    with db.get_session() as sess:
        return sess.get(CartDB, cart_id).contents


def query_all_paginated(
    customer: str,
    sku: str,
    order_by: str,
    order_asc: bool,
    limit: int,
    page: int,
) -> SearchResponse:
    """Return all orders corresponding to the passed search params"""
    offset = page * limit
    order_by = order_by if order_asc else desc(order_by)
    with db.get_session() as sess:
        query = sess.query(CartDB, CartContentDB).join(CartContentDB)
        if customer:
            query = query.filter(CartDB.customer_name.icontains(customer))
        if sku:
            query = query.filter(CartContentDB.item_sku.icontains(sku))
        query = query.order_by(order_by).offset(offset).limit(limit)

        results = [
            {
                "line_item_id": item.id,
                "item_sku": item.item_sku,
                "customer_name": cart.customer_name,
                "line_item_total": item.line_item_total,
                "timestamp": item.updated_at,
            }
            for cart, item in query.all()
        ]

        return {
            "previous": str(page - 1) if page > 0 else "",
            "next": str(page + 1) if results else "",
            "results": results,
        }


def set_item_quantity(cart_id: int, item_sku: str, quantity: int):
    """Create/Update/Delete a cart content entry"""
    with db.get_session() as sess, sess.begin():
        query = (
            sess.query(CartContentDB)
            .where(CartContentDB.cart_id == cart_id)
            .where(CartContentDB.item_sku == item_sku)
        )

        res = query.one_or_none()
        if res:
            res.line_item_total = quantity
            if res.line_item_total == 0:
                query.delete()
        else:
            new_entry = CartContentDB(
                cart_id=cart_id, item_sku=item_sku, line_item_total=quantity
            )
            sess.add(new_entry)


def create_new_cart(customer: str):
    """Creates a new cart for the customer"""
    with db.get_session() as sess:
        new_cart = CartDB(customer_name=customer)
        with sess.begin():
            sess.add(new_cart)
        return new_cart.cart_id


def checkout_cart(cart_id: int, payment: str):
    """Add sale to ledger, update inventory and delete cart"""
    logger.info("Checking out cart %d -> %s", cart_id, payment)
    total_pot, total_gold = 0, 0

    with db.get_session() as sess, sess.begin():
        cart: CartDB = sess.get(CartDB, cart_id)

        item_list = []
        for item in cart.contents:
            tran = {
                "sku": item.item_sku,
                "quantity": item.line_item_total,
                "unit_price": item.sku_data.price,
            }
            item_list.append(tran)
            total_pot += tran["quantity"]
            total_gold += tran["unit_price"]

        inventory.sell_to(item_list, cart.customer_name)
    return {"total_potions_bought": total_pot, "total_gold_paid": total_gold}


def reset_progress(sess: db.Session):
    """Reset shop progress"""
    sess.query(CartDB).delete()
    sess.query(CartContentDB).delete()
    sess.query(ItemSkuDB).delete()
