"""
Nightmare LPmud Toll Bridges, River Crossings & Customs Inspection Engine.

Implements:
1. Municipal River Drawbridges & Toll Gates.
2. Road Crossing Toll payments ('paytoll').
3. Toll Gate Bailiff operations ('collecttoll', 'lowergate').
4. Customs inspections for contraband and smuggled goods ('customsinspect').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_toll_gate(location, name="Praxis River Drawbridge Gate", fee=5):
    """Spawns an interactive toll bridge barrier."""
    gate = create_object(Object, key=name, location=location)
    gate.db.is_toll_gate = True
    gate.db.toll_fee = fee
    gate.db.is_open = False
    gate.db.collected_tolls = 0
    gate.db.desc = f"A heavy timber drawbridge barrier suspended over churning river waters. Toll Crossing Fee: {fee} coins."
    return gate


def pay_bridge_toll(caller, gate_name=""):
    """Pays the crossing fare to lower the drawbridge."""
    room = caller.location
    if not room:
        return False, "You cannot pay tolls in the void."

    gate = None
    for obj in room.contents:
        if getattr(obj.db, "is_toll_gate", False):
            if not gate_name or gate_name.lower() in obj.key.lower():
                gate = obj
                break

    if not gate:
        return False, "There is no toll bridge or crossing gate here."

    fee = getattr(gate.db, "toll_fee", 5)
    coins = getattr(caller.db, "coins", 0) or 0

    if coins < fee:
        return False, f"The toll collector blocks the gate: \"Toll is {fee} copper coins! No coin, no crossing!\" (You have {coins})"

    caller.db.coins = coins - fee
    gate.db.collected_tolls = (getattr(gate.db, "collected_tolls", 0) or 0) + fee
    gate.db.is_open = True

    caller.msg(
        f"\n|Y[TOLL PAID]|n You drop {fee} coins into the iron toll collector's box.\n"
        f"|w*RUMBLE-CLANK!*|n Counterweights groans as the {gate.key} lowers into place!\n"
        "The bridge bailiff waves you forward: |c\"Pass in peace, wayfarer!\"|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} pays the toll fee; iron chains clank as {gate.key} lowers across the river!",
            exclude=[caller]
        )
    return True, "Toll paid."


def perform_customs_inspection(caller, target_char=None):
    """Customs inspection searching for illicit contraband in a traveler's pack."""
    target = target_char if target_char else caller

    contraband = [
        obj.key for obj in target.contents
        if getattr(obj.db, "is_contraband", False) or "contraband" in obj.key.lower()
    ]

    lines = [
        "|c" + "=" * 65 + "|n",
        f"|w               MUNICIPAL CUSTOMS INSPECTION: {target.key.upper()} |n",
        "|c" + "=" * 65 + "|n"
    ]

    if contraband:
        lines.append(" |R[CONTRABAND DETECTED!]|n")
        for item in contraband:
            lines.append(f"   |r* Prohibited Cargo:|n |w{item}|n")
        lines.append("\n |yBailiff Verdict:|n Confiscation & 50-coin smuggling citation recommended!")
    else:
        lines.append(" |g[MANIFEST CLEAR]|n")
        lines.append("   All saddlebags, crates, and bundles inspected. No illicit contraband found.")
        lines.append("\n |yBailiff Verdict:|n Traveler stamped and cleared for civic transit.")

    lines.append("|c" + "=" * 65 + "|n")
    return "\n".join(lines)

