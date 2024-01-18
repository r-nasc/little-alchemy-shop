from typing import Annotated

from fastapi import APIRouter, Depends

from src.api import auth
from src.application.carts import carts
from src.application.carts.schemas import (
    Cart,
    CartCheckout,
    CartContent,
    CartItem,
    NewCart,
    SearchResponse,
    SearchSortOptions,
    SearchSortOrder,
)

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

ValidCart = Annotated[Cart, Depends(carts.get_by_id)]


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.TIMESTAMP,
    sort_order: SearchSortOrder = SearchSortOrder.DESC,
) -> SearchResponse:
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku,
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    limit = 5
    page = int(search_page or 0)
    if sort_col == SearchSortOptions.TIMESTAMP:
        sort_col = "updated_at"
    ord_asc = sort_order == SearchSortOrder.ASC
    return carts.query_all_paginated(
        customer_name, potion_sku, sort_col, ord_asc, limit, page
    )


@router.post("/")
def create_cart(new_cart: NewCart):
    """Creates a new shopping cart"""
    return {"cart_id": carts.create_new_cart(new_cart.customer)}


@router.get("/{cart_id}", response_model=list[CartContent])
def get_cart(cart: ValidCart):
    """Returns an existing shopping cart"""
    return carts.get_contents_by_id(cart.cart_id)


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(item_sku: str, cart_item: CartItem, cart: ValidCart):
    """Update item quantity in cart"""
    carts.set_item_quantity(cart.cart_id, item_sku, cart_item.quantity)
    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_checkout: CartCheckout, cart: ValidCart):
    """Updates the shop's inventory and deletes the cart"""
    return carts.checkout_cart(cart.cart_id, cart_checkout.payment)
