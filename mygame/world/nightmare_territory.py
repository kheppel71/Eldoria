"""
Nightmare LPmud Guild Territory Control & Stronghold System.

Implements:
1. Strategic Territory Nodes and War Banners.
2. Contested Territory Capture ('claim territory' / 'plant banner').
3. Regional combat buffs (+10% XP/Healing/Damage) for controlling guild members.
4. Realm Territory Overview ('territories').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


# Global registry of strategic territory control points
TERRITORIES = {
    "hive_crossroads": {
        "name": "Sigil Hive Ward Crossroads",
        "desc": "The central crossroads connecting the slum alleyways, bustling with underworld activity.",
        "controlling_guild": "Rogue",
        "buff": "+15% Stealth & Poison Potency"
    },
    "cathedral_gates": {
        "name": "High Cathedral Outer Sanctuary",
        "desc": "The marble gateway leading to the sacred cathedral steps.",
        "controlling_guild": "Cleric",
        "buff": "+20% Healing & Holy Radiant Smite Damage"
    },
    "high_barracks": {
        "name": "High Tower War Gates",
        "desc": "The iron portcullis guarding the garrison barracks.",
        "controlling_guild": "Fighter",
        "buff": "+15% Melee Armor & Kick Damage"
    },
    "arcane_library": {
        "name": "The Great Spire Archives",
        "desc": "The ancient sanctum holding arcane leyline nexus energies.",
        "controlling_guild": "Mage",
        "buff": "+20% Spell Damage & Mana Regeneration"
    }
}


def claim_territory(caller, node_key):
    """Claims a strategic territory node for caller's guild."""
    node = TERRITORIES.get(node_key)
    if not node:
        return False, f"Unknown territory node '{node_key}'."

    guild = getattr(caller.db, "guild", None)
    if not guild or guild == "Adventurer":
        return False, "You must be enrolled in an established Guild to claim territories!"

    current = node.get("controlling_guild")
    if current == guild:
        return False, f"{node['name']} is already under the sovereign control of the {guild} Guild!"

    # Successfully claim
    node["controlling_guild"] = guild

    caller.msg(f"\n|Y*** TERRITORY CONQUERED! ***|n")
    caller.msg(f"|yYou plant the proud war banner of the |w{guild}|y Guild into the bedrock of {node['name']}!|n")
    caller.msg(f"|GRegional Perk Active:|n {node['buff']}\n")

    if caller.location:
        caller.location.msg_contents(
            f"|r{caller.key} raises the banner of the {guild} Guild, claiming sovereign control of this territory!|n",
            exclude=[caller]
        )

    return True, f"Claimed {node['name']} for {guild}."


def get_regional_guild_buff(char, location):
    """Checks if character's guild controls the current location for bonus buffs."""
    if not location or not hasattr(char, "db"):
        return None

    char_guild = getattr(char.db, "guild", None)
    if not char_guild:
        return None

    for node_k, data in TERRITORIES.items():
        if data.get("controlling_guild") == char_guild:
            if node_k in location.key.lower() or data["name"].lower() in location.key.lower():
                return data["buff"]
    return None

