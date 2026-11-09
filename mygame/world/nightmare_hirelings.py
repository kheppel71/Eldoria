"""
Nightmare LPmud Mercenary Hirelings & Traveling Companions Engine.

Implements:
1. Tavern Sellswords and Traveling Companions:
   - Duran the Ironclad (Vanguard Tank)
   - Lyra Whisperwind (Woodland Scout)
   - Eldrin the Spark (Hedge Pyromancer)
2. Daily coin hiring mechanics ('hire <mercenary>').
3. Tactical command orders ('order <mercenary> <follow|attack|guard>').
4. Companion dismissal ('dismiss <mercenary>').
"""

from evennia.utils.create import create_object
from typeclasses.characters import Character

HIRELING_ROSTER = {
    "duran": {
        "name": "Duran the Ironclad",
        "role": "Vanguard Shield Tank",
        "level": 8,
        "hp": 220,
        "wage": 50,
        "desc": "A burly, scarred sellsword clad in heavy iron plate, resting his hand on a tower shield."
    },
    "lyra": {
        "name": "Lyra Whisperwind",
        "role": "Woodland Scout & Archer",
        "level": 8,
        "hp": 160,
        "wage": 60,
        "desc": "A lithe huntress with keen hazel eyes, carrying an oiled yew longbow and twin hunting knives."
    },
    "eldrin": {
        "name": "Eldrin the Spark",
        "role": "Hedge Pyromancer",
        "level": 9,
        "hp": 130,
        "wage": 75,
        "desc": "An eccentric traveling mage wrapped in ember-scorched robes, sparks dancing across his fingertips."
    }
}


def format_hirelings_display():
    """Formats available mercenary roster."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w                   PRAXIS MERCENARY & ADVENTURER GUILD            |n",
        "|c" + "=" * 70 + "|n"
    ]

    for key, data in HIRELING_ROSTER.items():
        lines.append(f"\n|Y{data['name']}|n [Role: |w{data['role']}|n - Lvl {data['level']}]")
        lines.append(f"  |yDaily Wage:|n {data['wage']} gold coins | |gMax Vitality:|n {data['hp']} HP")
        lines.append(f"  |x{data['desc']}|n")

    lines.append("\n|c" + "=" * 70 + "|n")
    lines.append("|xTo hire a companion: 'hire <name>' (requires sufficient gold)|n")
    return "\n".join(lines)


def hire_mercenary(caller, merc_key):
    """Contracts a mercenary to fight alongside the caller."""
    key = merc_key.strip().lower().split()[0]
    matched = next((k for k in HIRELING_ROSTER if key in k), None)

    if not matched:
        return False, f"Unknown mercenary '{merc_key}'. Type 'hirelings' to inspect the available sellswords."

    data = HIRELING_ROSTER[matched]
    wage = data["wage"]

    coins = getattr(caller.db, "coins", 0) or 0
    if coins < wage:
        return False, f"You cannot afford {data['name']}'s contract! Fee requires {wage} gold coins (you have {coins})."

    # Check if already hired
    for obj in (caller.location.contents if caller.location else []):
        if getattr(obj.db, "is_hireling", False) and getattr(obj.db, "employer", None) == caller:
            return False, f"You already have {obj.key} contracted under your banner!"

    caller.db.coins = coins - wage

    merc = create_object(Character, key=data["name"], location=caller.location)
    merc.db.is_hireling = True
    merc.db.employer = caller
    merc.db.hp = data["hp"]
    merc.db.max_hp = data["hp"]
    merc.db.level = data["level"]
    merc.db.desc = data["desc"]
    merc.db.stance = "guard"

    caller.msg(
        f"\n|Y[CONTRACT FORGED]|n You pay {wage} gold coins to {data['name']}.\n"
        f"|w{data['name']}|n salutes you firmly: |c\"My blade is yours, Commander. Lead the way.\"|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} signs a mercenary contract with {data['name']}!",
            exclude=[caller]
        )
    return True, f"Contracted {data['name']}."


def order_mercenary(caller, merc_name, command_str):
    """Issues tactical orders to an active hireling."""
    merc = None
    for obj in (caller.location.contents if caller.location else []):
        if getattr(obj.db, "is_hireling", False) and getattr(obj.db, "employer", None) == caller:
            if not merc_name or merc_name.lower() in obj.key.lower():
                merc = obj
                break

    if not merc:
        return False, "You do not have an active contracted mercenary here to command."

    cmd_clean = command_str.strip().lower()
    if "follow" in cmd_clean:
        merc.db.stance = "follow"
        caller.msg(f"\n|w{merc.key}|n nods: |c\"Understood, I am watching your flanks.\"|n\n")
        return True, "Order given."
    elif "guard" in cmd_clean:
        merc.db.stance = "guard"
        caller.msg(f"\n|w{merc.key}|n readies their shield: |c\"Standing guard over you, Commander.\"|n\n")
        return True, "Order given."
    elif "attack" in cmd_clean:
        target_name = cmd_clean.replace("attack", "").strip()
        caller.msg(f"\n|w{merc.key}|n lets out a warcry and readies weapons against {target_name or 'the enemy'}!|n\n")
        return True, "Order given."
    else:
        return False, "Orders available: 'order <hireling> follow', 'order <hireling> guard', 'order <hireling> attack <target>'"


def dismiss_mercenary(caller, merc_name=""):
    """Dismisses a contracted mercenary."""
    merc = None
    for obj in (caller.location.contents if caller.location else []):
        if getattr(obj.db, "is_hireling", False) and getattr(obj.db, "employer", None) == caller:
            if not merc_name or merc_name.lower() in obj.key.lower():
                merc = obj
                break

    if not merc:
        return False, "You do not have a contracted mercenary here to dismiss."

    caller.msg(f"\n|w{merc.key}|n bows respectfully: |c\"Our contract is fulfilled. Safe travels, friend.\"|n\n")
    if caller.location:
        caller.location.msg_contents(
            f"{merc.key} parts ways with {caller.key} and heads back to town.",
            exclude=[caller]
        )
    merc.delete()
    return True, "Mercenary dismissed."

