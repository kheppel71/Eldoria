"""
Nightmare LPmud Merchant Haggling, Dynamic Stock & Peddler System.

Implements:
1. Charisma-based Haggling ('haggle <item>').
2. Dynamic second-hand consignment inventory on merchants.
3. Wandering Peddlers selling trade goods and traveling sundries.
"""

import random
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.objects import Object


PEDDLER_WARES = [
    ("Iron Lockpick", 20, "A slender, hardened pick used by rogues to bypass tumblers."),
    ("Granite Whetstone", 15, "A coarse whetstone for honing blade edges in the field."),
    ("Empty Crystal Vial", 10, "A clean glass phial for brewing alchemical draughts."),
    ("Tinderbox & Torch", 5, "Flint, steel, and a pitch-soaked wooden torch for illumination."),
    ("Heavy Travel Cloak", 30, "A durable, weather-resistant woolen traveling cloak.")
]


def create_wandering_peddler(location, name="Koren the Peddler"):
    """Spawns a wandering merchant with traveling goods."""
    peddler = create_object(Character, key=name, location=location)
    peddler.db.desc = "A shrewd, weather-worn traveling merchant with a massive wicker pack strapped to his shoulders."
    peddler.db.is_peddler = True
    peddler.db.wares = [
        {"name": n, "price": p, "desc": d} for n, p, d in PEDDLER_WARES
    ]
    peddler.db.consignment_stock = []
    return peddler


def haggle_price(caller, base_price, is_buying=True):
    """
    Applies Charisma-based haggling modifier to purchase or sale price.
    """
    cha = caller.db.cha or 10
    roll = cha + random.randint(1, 20)

    if roll >= 22:
        discount = 0.25
        caller.msg("|G[MASTERFUL HAGGLE]|n With charming eloquence and silver-tongued wit, you negotiate a 25% better deal!|n")
    elif roll >= 16:
        discount = 0.15
        caller.msg("|g[SUCCESSFUL HAGGLE]|n The merchant nods grudgingly, agreeing to a 15% price adjustment.|n")
    else:
        discount = 0.0
        caller.msg("|yThe merchant chuckles and shakes their head: 'Firm price, take it or leave it, traveler.'|n")

    if is_buying:
        final_price = max(1, int(base_price * (1.0 - discount)))
    else:
        final_price = int(base_price * (1.0 + discount))

    return final_price


def peddler_buy_item(caller, peddler, item_name):
    """Buys an item from the peddler's wares."""
    if not getattr(peddler.db, "is_peddler", False):
        return False, f"{peddler.key} is not a merchant or peddler."

    wares = peddler.db.wares or []
    target_ware = next((w for w in wares if item_name.lower() in w["name"].lower()), None)
    if not target_ware:
        # Check consignment
        cons = peddler.db.consignment_stock or []
        target_ware = next((w for w in cons if item_name.lower() in w["name"].lower()), None)

    if not target_ware:
        return False, f"{peddler.key} does not have '{item_name}' in stock."

    price = haggle_price(caller, target_ware["price"], is_buying=True)
    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}

    if coins.get("gold", 0) < price:
        return False, f"You need {price} Gold to purchase {target_ware['name']} (You have {coins.get('gold', 0)} Gold)."

    coins["gold"] -= price
    caller.db.coins = coins

    # Create purchased item
    item = create_object(Object, key=target_ware["name"], location=caller)
    item.db.desc = target_ware.get("desc", "A purchased trade item.")
    item.db.value = target_ware["price"]

    caller.msg(f"|yYou purchase {item.key} from {peddler.key} for {price} Gold!|n")
    return True, "Purchased."

