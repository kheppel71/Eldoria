"""
Nightmare LPmud Merchant Caravans & Highwayman Ambush Engine.

Implements:
1. Scheduled Merchant Trade Caravans:
   - Praxis to High Desert Outpost (Silks & Spices)
   - Praxis to Coastal Port Docks (Iron Ingots & Ale)
   - Praxis to Catacombs Encampment (Holy Oil & Silver)
2. Caravan Escort Guard duty ('escort').
3. Roadside Highwayman & Bandit Ambushes ('defendwagon').
4. Cargo crates and gold pay rewards for successful escort.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

CARAVAN_ROUTES = {
    "praxis_desert": {
        "title": "Praxis to High Desert Outpost",
        "cargo": "Silk Bales & Exotic Spices",
        "destination": "High Desert Outpost",
        "reward_coins": 85,
        "threat": "Moderate",
        "desc": "A convoy of reinforced wooden wagons pulled by stout draft horses loaded with silk and spice crates."
    },
    "praxis_docks": {
        "title": "Praxis to Coastal Port Docks",
        "cargo": "Smelted Iron Bars & Dwarven Stout",
        "destination": "Sunken Coast Docks",
        "reward_coins": 100,
        "threat": "High",
        "desc": "Two heavy iron-plated dray wagons loaded with smelted metal and barrels bound for maritime ships."
    },
    "praxis_catacombs": {
        "title": "Praxis to Catacomb Encampment",
        "cargo": "Consecrated Oils & Silvered Weapons",
        "destination": "Cemetery Crypt Entrance",
        "reward_coins": 125,
        "threat": "Very High",
        "desc": "A holy templar wagon bearing sacred censers and weapon crates heading into the haunted dark."
    }
}

ACTIVE_ESCORT_GUARDS = {}


def format_caravans_display():
    """Formats caravan departure board."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w                   PRAXIS MERCHANT TRADE CARAVANS                 |n",
        "|c" + "=" * 70 + "|n"
    ]

    for key, data in CARAVAN_ROUTES.items():
        lines.append(f"\n|Y[ROUTE]|n |w{data['title']}|n")
        lines.append(f"  |yManifest Cargo:|n {data['cargo']}")
        lines.append(f"  |mDestination:|n {data['destination']} | |rThreat Level:|n {data['threat']}")
        lines.append(f"  |gEscort Bounty:|n {data['reward_coins']} gold coins")
        lines.append("  " + "-" * 66)

    lines.append("|c" + "=" * 70 + "|n")
    lines.append("|xTo enlist as a wagon guard: 'escort <praxis_desert|praxis_docks|praxis_catacombs>'|n")
    return "\n".join(lines)


def join_caravan_escort(caller, route_key="praxis_desert"):
    """Enlists character as an escort guard for a trade caravan."""
    key = route_key.strip().lower()
    matched = next((k for k in CARAVAN_ROUTES if key in k), None)

    if not matched:
        return False, f"Unknown caravan route '{route_key}'. Type 'caravans' to inspect available trade lines."

    data = CARAVAN_ROUTES[matched]
    ACTIVE_ESCORT_GUARDS[caller.id] = {
        "route_key": matched,
        "data": data,
        "ambush_cleared": False
    }

    caller.msg(
        f"\n|Y[CARAVAN ENLISTMENT]|n You take up your post as an escort guard for the |w{data['title']}|n!\n"
        f"The caravan master cracks the whip as the heavy wagon rummages into the perilous road.\n"
        f"|yKeep your eyes peeled for roadside highwaymen!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} joins the escort guard for the {data['title']}.",
            exclude=[caller]
        )
    return True, f"Enlisted for {data['title']}."


def trigger_caravan_defense(caller):
    """Triggers highwayman defense encounter for active escort guard."""
    if caller.id not in ACTIVE_ESCORT_GUARDS:
        return False, "You are not currently escorting any active merchant caravan! Type 'caravans' to enlist."

    guard_data = ACTIVE_ESCORT_GUARDS[caller.id]
    route_info = guard_data["data"]
    room = caller.location

    if not guard_data["ambush_cleared"]:
        # Spawn ambush bandit
        bandit_names = ["Highwayman Crossbowman", "Bandit Cutthroat", "Roadside Marauder"]
        bname = random.choice(bandit_names)
        bandit = create_object(Object, key=bname, location=room)
        bandit.db.hp = 90
        bandit.db.max_hp = 90
        bandit.db.desc = "A hooded highwayman brandishing a stained blade, trying to hijack the trade wagon!"

        guard_data["ambush_cleared"] = True
        caller.msg(
            f"\n|R[AMBUSH!]|n Shouts echo from the trees: |r\"Halt and hand over the wagon!\"|n\n"
            f"|rA {bandit.key} leaps onto the road, attacking the convoy! Defend the cargo!|n\n"
        )
        if room:
            room.msg_contents(
                f"|r*WHISTLE!* Highwaymen ambush the caravan! {caller.key} draws steel to protect the wagon!|n",
                exclude=[caller]
            )
        return True, "Ambush triggered."

    else:
        # Caravan reaches destination safely!
        reward = route_info["reward_coins"]
        caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + reward
        ACTIVE_ESCORT_GUARDS.pop(caller.id, None)

        crate = create_object(Object, key="Merchant Guild Bounty Crate", location=caller)
        crate.db.desc = f"A wooden crate sealed with pitch stamped with the Praxis Merchant Guild seal. Contains rewards from {route_info['title']}."

        caller.msg(
            f"\n|G[CARAVAN ESCORT SUCCESS]|n\n"
            f"The convoy arrives securely at |w{route_info['destination']}|n!\n"
            f"The caravan master thanks you and hands you |y{reward} gold coins|n and a |w{crate.key}|n!\n"
        )
        if room:
            room.msg_contents(
                f"{caller.key} successfully delivers the merchant trade caravan to its destination!",
                exclude=[caller]
            )
        return True, "Caravan escorted successfully."

