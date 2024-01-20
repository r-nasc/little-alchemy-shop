from src.application.bottler.schemas import PotionInventory
from src.application.inventory import inventory

PROFIT = 2
MIN_STOCK = 10
MIN_PRICE = 20
ML_PER_BOTTLE = 100


def receive_delivery(potions: list[PotionInventory]):
    """Receive bottled potions and deduct ingredients from stock"""
    inventory.add_potions_sub_ingredients(potions)
    return "OK"


def choose_potions_to_bottle() -> list[PotionInventory]:
    """Choose what to bottle based on current stock"""
    bottle_plan = []
    colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]

    cost_ml = inventory.get_cost_per_ml()
    stock_ml = inventory.get_available_stock_ml()
    for pot in inventory.get_available_stock(potions_only=True):
        if pot.quantity >= MIN_STOCK:
            continue

        qty_should_make = MIN_STOCK - pot.quantity
        qty_can_make = min(
            stock_ml[col] // max(getattr(pot, col, 0), 0.0001) for col in colors
        )
        qty_to_make = min(qty_can_make, qty_should_make)

        cost_to_make = 0
        ingredients = [getattr(pot, col, 0) for col in colors]
        for i, val in enumerate(ingredients):
            stock_ml[colors[i]] -= val
            cost_to_make += cost_ml[colors[i]] * val
        bottle_plan.append({"potion_type": ingredients, "quantity": qty_to_make})

        sku = inventory.get_sku_from_ingredients(ingredients)
        selling_price = max(cost_to_make * PROFIT, MIN_PRICE)
        inventory.update_sku_data(sku, selling_price, ingredients)
    return bottle_plan
