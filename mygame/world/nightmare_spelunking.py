"""
Nightmare LPmud Wilderness Spelunking, Rappelling & Chasm Crossing Engine.

Implements:
1. Spelunking Gear:
   - Coil of Braided Silk Rope
   - Steel Pitons & Grappling Hook
2. Rope Anchoring on stone ledges and sinkhole edges ('tierope').
3. Rappelling down into vertical subterranean abysses and ascends ('rappel <down|up>').
4. Securing chasm rope traverse bridges ('anchorbridge').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_climbing_rope(location, name="Coil of Braided Silk Rope"):
    """Spawns an expedition climbing rope."""
    rope = create_object(Object, key=name, location=location)
    rope.db.is_rope = True
    rope.db.desc = "A 100-foot coil of weather-proof braided mountain silk rope with an iron carabiner and pitons."
    return rope


def tie_rappelling_rope(caller, anchor_name=""):
    """Anchors climbing rope to a stone outcrop or cavern ledge."""
    room = caller.location
    if not room:
        return False, "You cannot anchor rope in the void."

    # Check for rope
    rope = None
    for obj in caller.contents:
        if getattr(obj.db, "is_rope", False) or "rope" in obj.key.lower():
            rope = obj
            break

    if not rope:
        return False, "You need a Coil of Climbing Rope in your pack to rig a rappelling line! ('tierope')"

    room.db.has_rope_line = True
    caller.msg(
        f"\n|Y[SPELUNKING RIG]|n You drive steel pitons into the solid rock with a hammer\n"
        f"and anchor your |w{rope.key}|n securely! The rope drops into the darkness below!\n"
        "|yYou may now 'rappel down' or 'rappel up'.|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} hammers pitons into the rock face and rigs a sturdy rappelling line.",
            exclude=[caller]
        )
    return True, "Rope anchored."


def execute_rappel(caller, direction="down"):
    """Rappels along an anchored rope line."""
    room = caller.location
    if not room or not getattr(room.db, "has_rope_line", False):
        return False, "There is no anchored rope line rigged here! Anchor one first with 'tierope'."

    dir_clean = direction.strip().lower()
    target_exit = None
    for ex in room.exits:
        if dir_clean in ex.key.lower() or dir_clean in ex.aliases:
            target_exit = ex
            break

    if not target_exit or not target_exit.destination:
        return False, f"There is no vertical cavern passage heading {direction} to rappel into."

    dest = target_exit.destination

    caller.msg(
        f"\n|c*WHIRRRR!* Slipping your brake hand into leather gloves, you kick off the rock wall\n"
        f"and rappel smoothly {direction} through the echoing darkness into {dest.key}!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} grips the rappelling line, kicks off the precipice, and slides {direction} into the dark.",
            exclude=[caller]
        )

    caller.move_to(dest, quiet=True)
    dest.msg_contents(f"{caller.key} rappels down gracefully from the overhead abyss!", exclude=[caller])
    return True, f"Rappeiled {direction} to {dest.key}."


def anchor_chasm_bridge(caller):
    """Secures a tensioned rope traverse across a cavern chasm."""
    room = caller.location
    if not room:
        return False, "You cannot rig a bridge in the void."

    # Look for rope
    rope = None
    for obj in caller.contents:
        if getattr(obj.db, "is_rope", False) or "rope" in obj.key.lower():
            rope = obj
            break

    if not rope:
        return False, "You need climbing rope to rig a chasm traverse bridge."

    room.db.has_rope_bridge = True
    caller.msg(
        f"\n|G[CHASM TRAVERSE]|n You fire a weighted grappling hook across the chasm gap!\n"
        "It catches a boulder on the opposite rim. You tension the lines with a block-and-tackle,\n"
        "creating a secure |wRope Traverse Bridge|n for your party to cross!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} fires a grappling hook and tensions a sturdy rope bridge across the chasm abyss!",
            exclude=[caller]
        )
    return True, "Chasm bridge secured."

