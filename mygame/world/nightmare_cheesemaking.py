"""
Nightmare LPmud Artisan Cheesemaking, Dairy Churning & Cellar Aging Engine.

Implements:
1. Pasture Livestock Milking ('milklivestock') yielding Pails of Rich Farm Milk.
2. Dairy Butter Churning ('churnbutter') producing Crocks of Sweet Butter.
3. Artisan Cheese Pressing ('presscheese'):
   - Sharp Highland Cheddar
   - Veined Blue Stilton
   - Smoked Cave Gouda
4. Cellar Aging & Maturation ('agecheese') granting the 'Pastoral Sustenance' buff.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

CHEESE_TYPES = {
    "cheddar": {
        "name": "Sharp Highland Cheddar Wheel",
        "rind": "Waxed Red Cloth",
        "flavor": "tangy, nutty, and crumbly with salt crystals",
        "stamina_buff": 25,
        "desc": "A dense golden wheel of clothbound cheddar aged to sharp, crystalline perfection."
    },
    "stilton": {
        "name": "Veined Blue Stilton Wheel",
        "rind": "Natural Crusty Rind",
        "flavor": "creamy, piquantly pungent, and deeply rich",
        "stamina_buff": 30,
        "desc": "A cylindrical wheel pierced with delicate ribbons of royal blue penicillium roqueforti."
    },
    "gouda": {
        "name": "Smoked Cave Gouda Wheel",
        "rind": "Yellow Waxed Shell",
        "flavor": "sweet butterscotch and fragrant hickory smoke",
        "stamina_buff": 20,
        "desc": "A smooth wheel of Gouda cheese cold-smoked over dried applewood in a stone subterranean cellar."
    }
}


def milk_farm_livestock(caller):
    """Milks dairy cows or mountain goats in rural or pasture areas."""
    room = caller.location
    if not room:
        return False, "You cannot milk livestock in the void."

    pail = create_object(Object, key="Pail of Rich Farm Milk", location=caller)
    pail.db.is_milk = True
    pail.db.desc = "A foaming tin pail brimming with warm, unpasteurized sweet cream milk."

    caller.msg("\n|Y[DAIRY FARMING]|n You gently milk the dairy livestock into a tin pail!\n")
    if room:
        room.msg_contents(f"{caller.key} milks the pasture livestock, filling a foaming tin pail.", exclude=[caller])
    return True, "Milk collected."


def churn_dairy_butter(caller):
    """Churns milk cream in a wooden churn into sweet salted butter."""
    milk = None
    for obj in caller.contents:
        if getattr(obj.db, "is_milk", False) or "milk" in obj.key.lower():
            milk = obj
            break

    if not milk:
        return False, "You need a Pail of Rich Farm Milk in your pack to churn butter! Use 'milklivestock' first."

    milk.delete()
    crock = create_object(Object, key="Crock of Salted Farm Butter", location=caller)
    crock.db.is_food = True
    crock.db.desc = "A glazed earthenware crock filled with creamy, golden farm butter patted with sea salt."

    caller.msg("\n|Y[BUTTER CHURN]|n You pump the wooden churn dash up and down until rich golden butter breaks!\n")
    return True, "Butter churned."


def press_artisan_cheese(caller, cheese_choice="cheddar"):
    """Presses salted curds in a cheese press to form a wax-sealed wheel."""
    key = cheese_choice.strip().lower()
    matched = next((k for k in CHEESE_TYPES if key in k), None)

    if not matched:
        opts = ", ".join(CHEESE_TYPES.keys())
        return False, f"Unknown cheese variety '{cheese_choice}'. Options: {opts}"

    data = CHEESE_TYPES[matched]

    # Look for milk
    milk = None
    for obj in caller.contents:
        if getattr(obj.db, "is_milk", False) or "milk" in obj.key.lower():
            milk = obj
            break

    if not milk:
        return False, "You need a Pail of Milk to separate curds and press cheese!"

    milk.delete()

    wheel = create_object(Object, key=data["name"], location=caller)
    wheel.db.is_cheese = True
    wheel.db.is_food = True
    wheel.db.is_aged = False
    wheel.db.buff_val = data["stamina_buff"]
    wheel.db.desc = data["desc"]

    caller.msg(
        f"\n|G[CHEESEMAKING SUCCESS]|n You inoculate the curds, pack them into a beechwood hoop, and apply press weights!\n"
        f"You produce a fine |w{wheel.key}|n!\n"
        "|yUse 'agecheese' to cellar-mature the cheese for enhanced flavor and stamina buffs!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} presses salted curds into a clothbound {wheel.key}.",
            exclude=[caller]
        )
    return True, f"Pressed {wheel.key}."


def age_cheese_in_cellar(caller):
    """Ages a wheel of cheese on cool subterranean cellar racks."""
    cheese = None
    for obj in caller.contents:
        if getattr(obj.db, "is_cheese", False) and not getattr(obj.db, "is_aged", False):
            cheese = obj
            break

    if not cheese:
        return False, "You do not have any fresh, un-aged cheese wheels in your pack to cellar-mature!"

    cheese.db.is_aged = True
    old_name = cheese.key
    cheese.key = f"Vintage Cellar-Aged {old_name}"

    caller.msg(
        f"\n|Y[CELLAR MATURATION]|n You place {old_name} upon cedar slatted racks in the cool subterranean vault.\n"
        f"The rinds form noble molds and the interior develops savory crystals! Now a |w{cheese.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} retrieves a perfectly matured wheel of vintage cheese from the cellar racks.",
            exclude=[caller]
        )
    return True, "Cheese aged."

