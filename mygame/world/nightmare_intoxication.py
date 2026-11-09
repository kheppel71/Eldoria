"""
Nightmare LPmud Tavern Intoxication, Drunken Slur & Liquid Courage Engine.

Implements:
1. Dynamic tavern drink library (Stout, Whiskey, Mead, Spiced Wine, Black Coffee).
2. Progressive Intoxication Tiers (Sober, Buzzed, Drunk, Wasted, Passed Out).
3. Realistic Drunken Speech Filter for dialog ('s' -> 'sh', doubled vowels, hiccups).
4. Liquid Courage damage reduction buff & Dexterity impairment.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

DRINKS = {
    "stout": {
        "name": "Dwarven Triple Stout",
        "proof": 25,
        "cost": 4,  # Silver
        "desc": "A thick, jet-black ale with a frothy tan head, smelling of roasted barley and oak."
    },
    "whiskey": {
        "name": "Dragon's Breath Whiskey",
        "proof": 45,
        "cost": 10,
        "desc": "A blistering amber liquor distilled in volcanic barrels. It burns all the way down."
    },
    "mead": {
        "name": "Golden Honey Mead",
        "proof": 15,
        "cost": 3,
        "desc": "A sweet, fragrant mead fermented from wild clover honey."
    },
    "wine": {
        "name": "Elven Spiced Wine",
        "proof": 20,
        "cost": 6,
        "desc": "A delicate ruby wine infused with cinnamon, cloves, and star anise."
    },
    "coffee": {
        "name": "Bitter Black Coffee",
        "proof": -30,
        "cost": 2,
        "desc": "A steaming, pitch-black brew guaranteed to shock the senses and sober the mind."
    }
}


def apply_drunken_slur(text, intoxication):
    """Transforms spoken text with classic LPmud drunken slurs."""
    if intoxication < 30:
        return text

    words = text.split()
    slurred_words = []

    for w in words:
        mod = w
        # Slur s into sh
        mod = mod.replace("s", "sh").replace("S", "Sh")
        mod = mod.replace("th", "ff")

        # Double vowels occasionally if heavily drunk
        if intoxication >= 60 and random.random() < 0.25:
            mod = mod.replace("o", "oo").replace("a", "aa")

        slurred_words.append(mod)

    # Insert hiccups
    if intoxication >= 45 and random.random() < 0.40:
        idx = random.randint(0, len(slurred_words))
        hic = random.choice(["...*hic*...", "...*burp*...", "...*huck*..."])
        slurred_words.insert(idx, hic)

    return " ".join(slurred_words)


def consume_tavern_drink(caller, drink_key):
    """Consumes a tavern drink, updating intoxication and applying buffs."""
    key = drink_key.lower().strip()
    data = DRINKS.get(key)
    if not data:
        for d_k, d_val in DRINKS.items():
            if key in d_k or key in d_val["name"].lower():
                data = d_val
                key = d_k
                break

    if not data:
        caller.msg(f"The barkeep shrugs: 'We don't serve {drink_key} here. Try: {', '.join(DRINKS.keys())}'")
        return False, "Unknown drink."

    # Check silver coins
    cost = data["cost"]
    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    total_silver = (coins.get("gold", 0) * 10) + coins.get("silver", 0)

    if total_silver < cost:
        return False, f"You need {cost} Silver for a {data['name']} (You have {total_silver} Silver)."

    # Deduct cost
    total_silver -= cost
    coins["gold"] = total_silver // 10
    coins["silver"] = total_silver % 10
    caller.db.coins = coins

    # Adjust intoxication
    cur_intox = getattr(caller.db, "intoxication", 0) or 0
    new_intox = max(0, min(100, cur_intox + data["proof"]))
    caller.db.intoxication = new_intox

    if data["proof"] < 0:
        caller.msg(f"\n|cYou drink the steaming {data['name']}. The bitter roast clears your head! (Intoxication: {new_intox}%)|n\n")
    else:
        caller.msg(f"\n|yYou slam back the {data['name']}! A warm, fiery buzz spreads through your veins! (Intoxication: {new_intox}%)|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} drinks a goblet of {data['name']}.",
            exclude=[caller]
        )

    # Liquid courage check
    if new_intox >= 60:
        caller.db.liquid_courage = True
        caller.msg("|R[LIQUID COURAGE]|n You feel completely invincible! (+15% Physical Damage Absorption)|n")
    else:
        caller.db.liquid_courage = False

    return True, "Drank."

