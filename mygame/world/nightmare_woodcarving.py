"""
Nightmare LPmud Artisan Woodcarving, Whittling & Instrument Crafting Engine.

Implements:
1. Whittling knife heartwood carving ('whittle'):
   - Polished Briar Smoking Pipe
   - Carved Totemic Owl Talisman
2. Acoustic Pine Flute crafting ('carveflute').
3. Master Spruce Bardic Lute crafting ('carvelute') boosting musical ballads.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

WHITTLE_ITEMS = {
    "pipe": {
        "name": "Polished Briar Smoking Pipe",
        "desc": "A handsome smoking pipe carved from flame-grained briar wood with a curved horn mouthpiece."
    },
    "talisman": {
        "name": "Carved Totemic Owl Talisman",
        "desc": "A smooth wooden pendant etched with the likeness of a horned owl with obsidian inlay eyes."
    },
    "staff": {
        "name": "Carved Ironwood Walking Staff",
        "desc": "A sturdy, balanced hiking staff spiraled with vine engravings, capped with a copper ferrule."
    }
}


def whittle_wooden_curio(caller, item_key="pipe"):
    """Whittles seasoned timber into a polished curio or pipe."""
    key = item_key.strip().lower()
    matched = next((k for k in WHITTLE_ITEMS if key in k), None)

    if not matched:
        opts = ", ".join(WHITTLE_ITEMS.keys())
        return False, f"Unknown whittling project '{item_key}'. Options: {opts}"

    data = WHITTLE_ITEMS[matched]
    curio = create_object(Object, key=data["name"], location=caller)
    curio.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[WHITTLING WORK]|n Drawing your whittling knife along the seasoned wood,\n"
        f"ribbons of sweet cedar curl to the floor as you fashion a |w{curio.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} whittles a block of wood with practiced strokes, shaping a fine {curio.key}.",
            exclude=[caller]
        )
    return True, f"Whittled {curio.key}."


def carve_wooden_flute(caller):
    """Bores and tunes an acoustic six-hole pine flute."""
    flute = create_object(Object, key="Hand-Carved Pine Flute", location=caller)
    flute.db.is_instrument = True
    flute.db.desc = "A six-holed transverse flute carved from mountain pine, producing pure, birdsong-like notes."

    caller.msg(
        f"\n|G[ACOUSTIC CRAFTING]|n You bore tone holes into a slender pine bough with a heated iron auger,\n"
        f"tuning the embouchure hole to true concert pitch! You craft a |w{flute.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} polishes and tests the tone holes of a hand-carved pine flute.",
            exclude=[caller]
        )
    return True, f"Crafted {flute.key}."


def carve_bardic_lute(caller):
    """Assembles a resonant spruce lute with gut strings."""
    coins = getattr(caller.db, "coins", 0) or 0
    if coins < 35:
        return False, "Crafting an acoustic lute requires 35 gold coins for specialized pegs, bridge, and gut strings."

    caller.db.coins = coins - 35
    lute = create_object(Object, key="Acoustic Spruce Bardic Lute", location=caller)
    lute.db.is_instrument = True
    lute.db.is_bardic_lute = True
    lute.db.desc = "An arched-back acoustic lute assembled from alternating ribs of maple and spruce, strung with twisted gut strings."

    caller.msg(
        f"\n|Y[MASTER LUTHIER]|n You bend maple ribs over a hot iron, book-match a spruce soundboard,\n"
        f"and string the instrument with twisted gut strings! You have constructed a magnificent |w{lute.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} plucks the sweet resonant strings of a newly crafted {lute.key}.",
            exclude=[caller]
        )
    return True, f"Crafted {lute.key}."

