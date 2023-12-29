from fastapi import APIRouter, Depends

from src.api import auth
from src.application import carts
from src.application.schemas import (
    CartCheckout,
    Cart,
    CartDbEntry,
    CartItem,
    NewCart,
    SearchSortOptions,
    SearchSortOrder,
)

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.TIMESTAMP,
    sort_order: SearchSortOrder = SearchSortOrder.DESC,
):
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

    # TODO: Implement
    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


@router.post("/")
def create_cart(new_cart: NewCart):
    """Creates a new shopping cart"""
    return {"cart_id": carts.create_new_cart(new_cart.customer)}


@router.get("/{cart_id}", response_model=list[CartDbEntry])
def get_cart(cart: Cart = Depends(carts.get_by_id)):
    """Returns an existing shopping cart"""
    return list(cart.contents.values())


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(
    item_sku: str, cart_item: CartItem, cart: Cart = Depends(carts.get_by_id)
):
    """Update item quantity in cart"""
    carts.set_item_quantity(cart.cart_id, item_sku, cart_item.quantity)
    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_checkout: CartCheckout, cart: Cart = Depends(carts.get_by_id)):
    """ """
    # TODO: Implement
    return {"total_potions_bought": 1, "total_gold_paid": 50}
