"""
Nightmare LPmud Spell Scribing & Magic Scroll Engine.

Implements:
1. Scribing memorized arcane incantations onto parchment ('scribescroll <spell>').
2. Creation of portable, single-use Spell Scrolls.
3. Reading scrolls ('readscroll <scroll>') allowing any class to unleash emergency magic.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object
from world.nightmare_core import SPELLS


def scribe_spell_scroll(caller, spell_key, parchment_obj):
    """Binds a known spell incantation into a physical parchment scroll."""
    key = spell_key.lower().strip()
    s_data = SPELLS.get(key)
    if not s_data:
        for s_k, data in SPELLS.items():
            if key in s_k:
                s_data = data
                key = s_k
                break

    if not s_data:
        caller.msg(f"Unknown spell '{spell_key}'. Available: {', '.join(SPELLS.keys())}")
        return False, "Unknown spell."

    mana_cost = s_data.get("mana", 15) * 2  # Scribing requires double normal mana
    mana = caller.db.mana or 0
    if mana < mana_cost:
        return False, f"You need at least {mana_cost} Mana to permanently scribe this scroll! (Requires {mana_cost} Mana)"

    caller.db.mana -= mana_cost
    parchment_obj.delete()

    s_name = key.capitalize()
    scroll = create_object(Object, key=f"Scroll of {s_name}", location=caller)
    scroll.db.desc = f"A crackling parchment scroll inscribed with the arcane chant: \"{s_data.get('chant', '')}\". (Use: readscroll {scroll.key})"
    scroll.db.is_scroll = True
    scroll.db.spell_key = key
    scroll.db.spell_data = s_data
    scroll.db.value = s_data.get("mana", 15) * 3
    scroll.db.weight = 1

    caller.msg(f"\n|Y[SCRIBE SUCCESS]|n Dipping your quill in iridescent ink, you bind the leylines of |w{s_name}|n into {scroll.key}!")
    caller.msg(f"|xIncantation inscribed:|n \"{s_data.get('chant', '')}\"\n")

    if caller.location:
        caller.location.msg_contents(
            f"Arcane runes glow brightly as {caller.key} finishes scribing a magic scroll.",
            exclude=[caller]
        )
    return True, "Scribed."


def read_magic_scroll(caller, scroll_obj, target=None):
    """Unleashes the magical incantation stored within the scroll."""
    if not getattr(scroll_obj.db, "is_scroll", False):
        return False, f"{scroll_obj.key} is not a magical spell scroll!"

    s_key = scroll_obj.db.spell_key
    s_data = scroll_obj.db.spell_data or SPELLS.get(s_key, {})
    chant = s_data.get("chant", "Invocatio!")

    target_obj = target or caller

    caller.msg(f"\n|MYou unfurl {scroll_obj.key} and read the glowing runes aloud: \"{chant}\"!|n")
    if caller.location:
        caller.location.msg_contents(
            f"|m{caller.key} reads from a magical scroll: \"{chant}\"! Brilliant arcane fire consumes the parchment!|n",
            exclude=[caller]
        )

    # Resolve effect
    if "min_heal" in s_data or s_data.get("school") == "Restoration":
        import random
        heal_amt = random.randint(s_data.get("min_heal", 35), s_data.get("max_heal", 65))
        target_obj.db.hp = min(target_obj.db.max_hp or 100, (target_obj.db.hp or 0) + heal_amt)
        target_obj.msg(f"|gCelestial healing radiance knits your flesh! (+{heal_amt} HP)|n")

    elif "min_dmg" in s_data:
        import random
        dmg = random.randint(s_data.get("min_dmg", 25), s_data.get("max_dmg", 50))
        target_obj.db.hp = max(0, (target_obj.db.hp or 0) - dmg)
        target_obj.msg(f"|rBlistering arcane energy slams into you from the scroll for {dmg} damage!|n")
        caller.msg(f"|GThe spell blast scorches {target_obj.key} for {dmg} damage!|n")

    elif "absorb" in s_data:
        absorb = s_data.get("absorb", 50)
        target_obj.db.stoneskin_absorb = (target_obj.db.stoneskin_absorb or 0) + absorb
        target_obj.msg(f"|yHardened bark and granite armor encases you! (+{absorb} Damage Absorption)|n")

    scroll_obj.delete()
    return True, "Read."

