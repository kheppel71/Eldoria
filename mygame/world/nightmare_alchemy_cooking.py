"""
Nightmare LPmud Alchemy Brewing & Campfire Cooking System.

Implements:
1. Potion Brewing with harvested herbs and reagents.
2. Campfire Cooking of raw butchered monster meats into field rations.
3. Consumable drinking/eating logic with stamina, health, and well-fed regeneration buffs.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


RECIPES = {
    "healing": {
        "name": "Flask of Healing Salve",
        "req": ["Kingsfoil"],
        "desc": "A viscous green draught brewed from crushed Kingsfoil. Restores 45 HP and mends wounded limbs.",
        "effect": "heal_hp",
        "power": 45
    },
    "mana": {
        "name": "Elixir of Mental Clarity",
        "req": ["Silverleaf"],
        "desc": "A shimmering azure elixir that revitalizes magical focus, restoring 40 Mana.",
        "effect": "heal_mana",
        "power": 40
    },
    "antidote": {
        "name": "Philter of Purity",
        "req": ["Frostmint"],
        "desc": "A crisp, cooling tonic that purges virulent toxins and venom from the blood.",
        "effect": "cure_poison",
        "power": 0
    },
    "stoneskin": {
        "name": "Draught of Ironbark",
        "req": ["Ironbark Root"],
        "desc": "An earthy brew that hardens flesh into rugged bark, absorbing 50 damage.",
        "effect": "stoneskin",
        "power": 50
    }
}


def brew_potion(caller, recipe_key):
    """Brews an alchemical potion from carried herbs."""
    key = recipe_key.lower().strip()
    # Match recipe
    recipe = None
    for r_k, data in RECIPES.items():
        if key in r_k or key in data["name"].lower():
            recipe = data
            break

    if not recipe:
        caller.msg(f"Unknown recipe '{recipe_key}'. Available: {', '.join(RECIPES.keys())}")
        return False, "Unknown recipe."

    # Verify reagents
    req_items = []
    inv = list(caller.contents)

    for req_name in recipe["req"]:
        found = next((o for o in inv if req_name.lower() in o.key.lower()), None)
        if not found:
            return False, f"You are missing the required herb: |y{req_name}|n."
        req_items.append(found)
        inv.remove(found)

    # Consume reagents
    for it in req_items:
        it.delete()

    # Create potion
    potion = create_object(Object, key=recipe["name"], location=caller)
    potion.db.desc = recipe["desc"]
    potion.db.is_potion = True
    potion.db.potion_effect = recipe["effect"]
    potion.db.potion_power = recipe["power"]
    potion.db.value = 35
    potion.db.weight = 1

    caller.msg(f"\n|G[ALCHEMICAL SUCCESS]|n You blend the herbs in your vial, brewing a {recipe['name']}!|n")
    caller.msg(f"|xEffect:|n {recipe['desc']}\n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} brews an alchemical draught over a portable flame.",
            exclude=[caller]
        )
    return True, "Brewed."


def cook_meat(caller, raw_meat):
    """Cooks raw monster meat into savory roasted field rations."""
    if "Meat" not in raw_meat.key and "Flank" not in raw_meat.key and "Venison" not in raw_meat.key:
        return False, f"{raw_meat.key} is not raw meat that can be cooked."

    m_name = raw_meat.key.replace("Chunk of Fresh ", "").replace("Raw ", "").strip()
    raw_meat.delete()

    ration = create_object(Object, key=f"Roasted {m_name} Steak", location=caller)
    ration.db.desc = f"A hearty, sizzling slice of roasted {m_name}, charred to perfection over flames."
    ration.db.is_food = True
    ration.db.stamina_heal = 50
    ration.db.hp_heal = 20
    ration.db.value = 15
    ration.db.weight = 1

    caller.msg(f"|yYou sear the meat over glowing embers until it is sizzling and delicious: |w{ration.key}|y!|n")
    if caller.location:
        caller.location.msg_contents(
            f"The mouthwatering aroma of roasted meat fills the air as {caller.key} cooks.",
            exclude=[caller]
        )
    return True, "Cooked."


def eat_ration(caller, ration):
    """Consumes cooked food to replenish vitals and apply well-fed buff."""
    if not getattr(ration.db, "is_food", False):
        return False, f"{ration.key} is not edible food!"

    stamina_heal = ration.db.stamina_heal or 40
    hp_heal = ration.db.hp_heal or 15

    caller.db.stamina = min(caller.db.max_stamina or 100, (caller.db.stamina or 0) + stamina_heal)
    caller.db.hp = min(caller.db.max_hp or 100, (caller.db.hp or 0) + hp_heal)
    caller.db.well_fed = True

    caller.msg(f"\n|gYou feast on {ration.key}! (+{stamina_heal} Stamina, +{hp_heal} HP)|n")
    caller.msg("|YYou feel thoroughly nourished and well-fed!|n\n")

    ration.delete()
    return True, "Eaten."

