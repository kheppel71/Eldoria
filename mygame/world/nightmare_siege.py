"""
Nightmare LPmud Siege Warfare, Battering Rams & Gate Breaching Engine.

Implements:
1. Fortified Gates & Portcullises with structural hit points.
2. Battering Ram mechanics and assault strikes ('ramgate').
3. Gate structural breaches ('breachwall') allowing passage into fortresses.
4. Defense repairs using timber beams and iron bracing ('repairgate').
5. Structural integrity inspection ('gatestatus').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_fortified_gate(location, name="Reinforced Iron-Banded Gate", hp=300):
    """Spawns an assaultable fortified fortress gate."""
    gate = create_object(Object, key=name, location=location)
    gate.db.is_siege_gate = True
    gate.db.gate_hp = hp
    gate.db.max_gate_hp = hp
    gate.db.is_breached = False
    gate.db.desc = f"A massive oak and iron-banded gate designed to withstand heavy siege assaults. Structural HP: {hp}/{hp}."
    return gate


def create_battering_ram(location, name="Heavy Iron-Capped Battering Ram"):
    """Spawns a heavy siege ram."""
    ram = create_object(Object, key=name, location=location)
    ram.db.is_battering_ram = True
    ram.db.ram_power = 75
    ram.db.desc = "A monstrous tree trunk shod with a snarling iron ram's head, hung by chains on a wheeled wooden scaffold."
    return ram


def assault_gate_with_ram(caller, target_name=""):
    """Drives a battering ram into a fortified gate."""
    room = caller.location
    if not room:
        return False, "You cannot assault from the void."

    # Look for gate
    gate = None
    for obj in room.contents:
        if getattr(obj.db, "is_siege_gate", False):
            if not target_name or target_name.lower() in obj.key.lower():
                gate = obj
                break

    if not gate:
        return False, "There is no fortified gate here to ram!"

    if gate.db.is_breached:
        return False, f"{gate.key} has already been reduced to splintered debris!"

    # Look for ram in room or inventory
    has_ram = any(
        getattr(obj.db, "is_battering_ram", False) or "ram" in obj.key.lower()
        for obj in (caller.contents + room.contents)
    )

    damage = 80 if has_ram else 30
    curr_hp = getattr(gate.db, "gate_hp", 300)
    new_hp = max(0, curr_hp - damage)
    gate.db.gate_hp = new_hp

    if new_hp <= 0:
        gate.db.is_breached = True
        caller.msg(
            f"\n|R*BOOOOOOOM! CRRRASH!*|n The massive iron ram smashes through the central timbers of {gate.key}!\n"
            "|wIron bands snap and beams fracture into kindling! The fortress gate is |RBREACHED|w!|n\n"
        )
        if room:
            room.msg_contents(
                f"|R*KABLAM!* {caller.key} leads the ram charge, shattering {gate.key} wide open! The breach is clear!|n",
                exclude=[caller]
            )
        return True, "Gate breached."
    else:
        caller.msg(
            f"\n|Y*THUUUUD!*|n The heavy battering ram slams into {gate.key}! (-{damage} Integrity)\n"
            f"Timber groans under the impact! Gate Integrity: |w{new_hp}/{gate.db.max_gate_hp} HP|n.\n"
        )
        if room:
            room.msg_contents(
                f"|r*THUD!* The battering ram strikes {gate.key} with thunderous force! ({new_hp}/{gate.db.max_gate_hp} HP)|n",
                exclude=[caller]
            )
        return True, "Gate damaged."


def repair_siege_gate(caller, target_name=""):
    """Repairs a damaged siege gate using timber and iron brackets."""
    room = caller.location
    gate = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_siege_gate", False):
            if not target_name or target_name.lower() in obj.key.lower():
                gate = obj
                break

    if not gate:
        return False, "There is no gate here to repair."

    curr_hp = getattr(gate.db, "gate_hp", 300)
    max_hp = getattr(gate.db, "max_gate_hp", 300)

    if curr_hp >= max_hp:
        return False, f"{gate.key} is already fully fortified at maximum integrity ({max_hp}/{max_hp} HP)."

    repaired = min(max_hp, curr_hp + 60)
    gate.db.gate_hp = repaired
    gate.db.is_breached = False

    caller.msg(
        f"\n|G[FORTIFICATION REPAIRS]|n You nail heavy oak struts across the fractured beams of {gate.key}!\n"
        f"Structural integrity restored to |w{repaired}/{max_hp} HP|n!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} reinforces {gate.key} with crossbeams and iron braces, repairing structural damage.",
            exclude=[caller]
        )
    return True, "Gate repaired."


def format_gate_status(caller, target_name=""):
    """Displays structural integrity of the local gate."""
    room = caller.location
    gate = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_siege_gate", False):
            if not target_name or target_name.lower() in obj.key.lower():
                gate = obj
                break

    if not gate:
        return "There is no fortified gate here to inspect."

    hp = getattr(gate.db, "gate_hp", 300)
    max_hp = getattr(gate.db, "max_gate_hp", 300)
    pct = int((hp / max_hp) * 100) if max_hp else 0
    status_str = "|rBREACHED|n" if getattr(gate.db, "is_breached", False) else "|gSECURE|n"

    lines = [
        "|c" + "=" * 65 + "|n",
        f"|w                   FORTIFIED GATE STATUS: {gate.key.upper()} |n",
        "|c" + "=" * 65 + "|n",
        f" |wDefense Condition:|n {status_str}",
        f" |yStructural Integrity:|n |w{hp}/{max_hp} HP|n (|c{pct}%|n)",
        f" |x{gate.db.desc}|n",
        "|c" + "=" * 65 + "|n"
    ]
    return "\n".join(lines)

