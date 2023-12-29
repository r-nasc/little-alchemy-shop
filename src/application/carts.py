from fastapi import HTTPException
from src.application.schemas import Cart, CartDB, CartDbEntry
from src import database as db


def get_by_id(cart_id: int) -> Cart:
    """Returns an existing cart or raises"""
    with db.get_session() as sess:
        cart: Cart = sess.get(CartDB, cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="CartNotFound")
        return cart


def set_item_quantity(cart_id: int, item_sku: str, quantity: int):
    """Create/Update/Delete a cart content entry"""
    with db.get_session() as sess, sess.begin():
        cart: CartDB = sess.get(CartDB, cart_id)

        if item_sku not in cart.contents:
            new_entry = CartDbEntry(item_sku=item_sku, quantity=quantity)
            cart.contents[item_sku] = new_entry.dict()
        else:
            if quantity == 0:
                del cart.contents[item_sku]
            else:
                cart.contents[item_sku]["quantity"] = quantity


def create_new_cart(customer: str):
    """Creates a new cart for the customer"""
    with db.get_session() as sess:
        new_cart = CartDB(contents={}, customer=customer)
        with sess.begin():
            sess.add(new_cart)
        return new_cart.cart_id
