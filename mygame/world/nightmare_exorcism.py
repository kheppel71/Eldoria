"""
Nightmare LPmud Cursed Relics, Haunted Idols & Holy Exorcism Engine.

Implements:
1. Cursed artifacts and haunted idols that afflict carriers with dread,
   stamina drain, and un-equippable binding curses.
2. Curse inspection ('curseinfo').
3. Holy Exorcism & Purification rites ('exorcise', 'purify') to banish
   demonic corruption and cleanse afflicted relics.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

CURSED_TEMPLATES = {
    "whispering_ring": {
        "name": "Ring of Whispering Agony",
        "slot": "ring",
        "curse_name": "Agony's Bind",
        "effect_desc": "Drains vital stamina and cannot be voluntarily removed while cursed.",
        "desc": "A heavy obsidian band etched with screaming faces that radiate malevolent spiritual chill."
    },
    "haunted_idol": {
        "name": "Haunted Obsidian Idol",
        "slot": "held",
        "curse_name": "Spectral Torment",
        "effect_desc": "Attracts restless spirits and casts deep paranoia onto the bearer.",
        "desc": "A grotesque gargoyle idol carved from basalt, oozing a faint black spiritual vapor."
    },
    "bloodthirsty_axe": {
        "name": "Cursed Bloodthirsty Greataxe",
        "slot": "right_hand",
        "curse_name": "Vampiric Thirst",
        "effect_desc": "Hungers constantly for blood, gnawing at its bearer's life force.",
        "desc": "A jagged greataxe of blackened steel, its blade pulsing like a beating heart."
    }
}


def create_cursed_relic(location, template_key="whispering_ring"):
    """Spawns an afflicted cursed artifact."""
    data = CURSED_TEMPLATES.get(template_key, CURSED_TEMPLATES["whispering_ring"])
    item = create_object(Object, key=data["name"], location=location)
    item.db.is_cursed = True
    item.db.curse_name = data["curse_name"]
    item.db.curse_desc = data["effect_desc"]
    item.db.slot = data["slot"]
    item.db.desc = data["desc"]
    return item


def is_cursed(item):
    """Checks whether an item is afflicted with a curse."""
    return bool(getattr(item.db, "is_cursed", False))


def inspect_curse(caller, item):
    """Reveals the nature of the dark curse on an item."""
    if not is_cursed(item):
        return f"{item.key} is free of any demonic corruption or malefic curses."

    lines = [
        f"|r[CURSED ARTIFACT]|n |w{item.key}|n",
        f"|mAffliction Name:|n {item.db.curse_name}",
        f"|yMalignant Effect:|n {item.db.curse_desc}",
        "|xPurification: Requires holy exorcism rites ('exorcise <item>') to break the binding.|n"
    ]
    return "\n".join(lines)


def perform_exorcism(caller, target_name=""):
    """Performs an exorcism ritual to cleanse a cursed item or remove a cursed bind."""
    if not target_name:
        return False, "What cursed relic or afflicted entity do you wish to exorcise?"

    target = caller.search(target_name, location=caller)
    if not target:
        # Check equipped slots or room
        if caller.location:
            target = caller.location.search(target_name)

    if not target:
        return False, f"Could not find '{target_name}' to exorcise."

    if not is_cursed(target):
        return False, f"{target.key} carries no lingering spiritual curse to banish."

    # Perform purification
    curse_title = target.db.curse_name
    target.db.is_cursed = False
    target.db.curse_name = None
    target.db.curse_desc = None
    target.db.is_cleansed = True

    # Rename to purified version
    old_name = target.key
    purified_name = old_name.replace("Cursed ", "").replace("Haunted ", "") + " (Cleansed)"
    target.key = purified_name

    caller.msg(
        f"\n|Y[HOLY EXORCISM]|n You call upon the sacred heavenly light, brandishing divine power!\n"
        f"|WGolden radiance washes over {old_name}, shattering the '{curse_title}'!|n\n"
        f"A black wailing vapor dissipates into thin air as the item is restored to |w{purified_name}|n!\n"
    )

    if caller.location:
        caller.location.msg_contents(
            f"|W*FLASH!* Brilliant divine light bursts from {caller.key}'s hands, banishing the dark spirit from {old_name}!|n",
            exclude=[caller]
        )

    return True, f"Successfully exorcised {old_name}."

