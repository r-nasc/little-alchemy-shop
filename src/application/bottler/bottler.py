from src.application.bottler.schemas import PotionInventory
from src.application.inventory import inventory


ML_PER_BOTTLE = 100


def get_sku_from_ingredients(potion_type: list[int]):
    col = potion_type
    return f"POTION_{col[0]}_{col[1]}_{col[2]}_{col[3]}"


def receive_delivery(potions: list[PotionInventory]):
    # bought_items = []
    # stock_used = [0, 0, 0, 0]
    # for pot in potions:
    #     item_sku = get_sku_from_ingredients(pot.potion_type)
    #     bought_items.append({"sku": item_sku, "quantity": pot.quantity, "unit_price": 0})
    #     for col, ml in enumerate(pot.potion_type):
    #         stock_used[col] += ml * pot.quantity

    # sold_items = []
    #     for pot in potions
    # ]

    # for pot in potions:
    #     inventory.update_sku_data(pot.sku, pot.price, pot.potion_type)
    # inventory.buy_batch_from(bought_items, "Bottler")

    return "OK"


def choose_potions_to_bottle() -> list[PotionInventory]:
    return {
        "potion_type": [100, 0, 0, 0],
        "quantity": 0,  # math.floor(inv.num_red_ml / ML_PER_BOTTLE),
    }
