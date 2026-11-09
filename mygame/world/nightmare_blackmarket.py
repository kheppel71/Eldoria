"""
Nightmare LPmud Underworld Black Market & Smuggler Dens Engine.

Implements:
1. Covert Shadow Password verification ('whisperpass <code>').
2. Restricted Contraband Catalog:
   - Master Skeleton Pickset
   - Flask of Midnight Neurotoxin
   - Forged Noble Transit Papers
   - Smuggled Shadow Silk Cloak
3. Illicit black market transactions ('blackmarket', 'smugglebuy <item>').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

ACTIVE_PASSPHRASE = "shadows keep no records"

BLACK_MARKET_INVENTORY = {
    "pickset": {
        "name": "Master Skeleton Pickset",
        "cost": 150,
        "desc": "A velvet roll containing tension wrenches and rake picks fashioned from spring steel, effortlessly bypassing complex tumblers."
    },
    "neurotoxin": {
        "name": "Flask of Midnight Neurotoxin",
        "cost": 180,
        "desc": "A prohibited dark glass flask dripping with lethal subterranean fungal neurotoxin."
    },
    "papers": {
        "name": "Forged Noble Transit Papers",
        "cost": 120,
        "desc": "Official vellum transit writs carrying a counterfeit wax seal of the High Council, bypassing city gate inspections."
    },
    "cloak": {
        "name": "Smuggled Shadow Silk Cloak",
        "cost": 220,
        "desc": "A hood and cloak woven from arachnid shadow silk that absorbs light, granting exceptional concealment."
    }
}


def verify_shadow_password(caller, phrase=""):
    """Whispers the shadow password to gain black market clearance."""
    clean = phrase.strip().lower()
    if clean == ACTIVE_PASSPHRASE.lower() or "shadows" in clean:
        caller.db.has_blackmarket_clearance = True
        caller.msg(
            "\n|x[SHADOW SENTRY]|n A hidden viewing slit slides open in the iron-banded door.\n"
            "A gravelly voice whispers: |c\"The shadows recognize you. Welcome to the Den.\"|n\n"
            "|wHeavy deadbolts slide back with a muffled CLACK. You may now trade at the 'blackmarket'.|n\n"
        )
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} whispers into a hidden iron grating; heavy bolts unlatch from within.",
                exclude=[caller]
            )
        return True, "Access granted."
    else:
        caller.msg(
            "\n|rA hollow click echoes behind the door. A cold voice rasps: \"Wrong words, wanderer. Walk away before you lose your purse.\"|n\n"
        )
        return False, "Access denied."


def format_blackmarket_display(caller):
    """Displays the illegal black market inventory."""
    if not getattr(caller.db, "has_blackmarket_clearance", False):
        return "|rThe black market sentries refuse to deal with you. You must provide the shadow password first! ('whisperpass <code>')|n"

    lines = [
        "|c" + "=" * 70 + "|n",
        "|x                   PRAXIS UNDERWORLD CONTRABAND BAZAAR            |n",
        "|c" + "=" * 70 + "|n"
    ]

    for key, data in BLACK_MARKET_INVENTORY.items():
        lines.append(f"\n|Y[{key.upper()}]|n |w{data['name']}|n")
        lines.append(f"  |yBlack Market Price:|n {data['cost']} gold coins")
        lines.append(f"  |x{data['desc']}|n")

    lines.append("\n|c" + "=" * 70 + "|n")
    lines.append("|xTo acquire contraband: 'smugglebuy <item_code>' (e.g. smugglebuy pickset)|n")
    return "\n".join(lines)


def purchase_contraband(caller, item_key=""):
    """Purchases an illegal contraband item from the black market."""
    if not getattr(caller.db, "has_blackmarket_clearance", False):
        return False, "You must whisper the shadow passphrase to access contraband! ('whisperpass <code>')"

    key = item_key.strip().lower()
    matched = next((k for k in BLACK_MARKET_INVENTORY if key in k), None)

    if not matched:
        opts = ", ".join(BLACK_MARKET_INVENTORY.keys())
        return False, f"Unknown contraband '{item_key}'. Options: {opts}"

    data = BLACK_MARKET_INVENTORY[matched]
    cost = data["cost"]
    coins = getattr(caller.db, "coins", 0) or 0

    if coins < cost:
        return False, f"The shadow fence demands {cost} gold coins (you have {coins}). No credit extended."

    caller.db.coins = coins - cost

    item = create_object(Object, key=data["name"], location=caller)
    item.db.is_contraband = True
    item.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[CONTRABAND ACQUIRED]|n You slide {cost} gold coins beneath the iron hatch.\n"
        f"A gloved hand pushes forward |w{item.key}|n wrapped in dark sacking.\n"
    )
    return True, f"Purchased {item.key}."

