"""
Nightmare LPmud Runecarving, Protective Wards & Explosive Sigil Engine.

Implements:
1. Protective Ward Inscriptions:
   - Rune of Alarming (Notifies carver on unauthorized entry)
   - Glyph of Frost Warding (Slows and freezes intruders)
   - Explosive Fire Sigil (Detonates for fiery blast damage)
2. Carving wards on room flagstones, door thresholds, and chests ('carverune', 'etchglyph').
3. Ward triggering and trap detonation.
4. Careful ward disarming ('disarmglyph').
"""

RUNE_TYPES = {
    "alarm": {
        "name": "Rune of Alarming",
        "effect": "alert",
        "desc": "A silver chime sigil that resonates telepathically with the carver whenever breached."
    },
    "frost": {
        "name": "Glyph of Frost Warding",
        "effect": "freeze",
        "desc": "An azure crystallizing snowflake glyph that flash-freezes intruders (-20 Stamina & chill)."
    },
    "explosive": {
        "name": "Explosive Fire Sigil",
        "effect": "blast",
        "desc": "A volatile crimson rune that ignites in a fiery blast wave dealing heavy concussive fire damage."
    }
}


def carve_ward(caller, ward_type="alarm", target_obj=None):
    """Etches a magical protective ward on the floor or an object."""
    type_clean = ward_type.strip().lower()
    matched = next((k for k in RUNE_TYPES if type_clean in k), None)

    if not matched:
        opts = ", ".join(RUNE_TYPES.keys())
        return False, f"Unknown ward type '{ward_type}'. Available runes: {opts}"

    data = RUNE_TYPES[matched]
    target = target_obj if target_obj else caller.location

    if not target:
        return False, "You cannot etch a ward into the void."

    # Store ward on target
    target.db.active_ward = {
        "type": matched,
        "name": data["name"],
        "carver": caller,
        "is_armed": True
    }

    caller.msg(
        f"\n|Y[RUNECARVING]|n You chisel intricate eldritch patterns into {target.key} and infuse it with mana!\n"
        f"|w{data['name']}|n now glows faintly upon {target.key} with protective vigilance!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} carves glowing magical runes of protection into {target.key}.",
            exclude=[caller]
        )
    return True, f"Etched {data['name']}."


def trigger_ward_check(target_entity, intruder):
    """Checks and triggers an active ward if breached by an uninvited character."""
    ward = getattr(target_entity.db, "active_ward", None)
    if not ward or not ward.get("is_armed", False):
        return False, "No active ward."

    carver = ward.get("carver")
    if carver == intruder:
        return False, "Carver bypasses own ward."

    ward_type = ward.get("type", "alarm")

    if ward_type == "alarm":
        intruder.msg(f"\n|C*CHIME!* As you step near {target_entity.key}, a silver chime echoes in your mind! An alarm rune was tripped!|n\n")
        if carver and carver.location:
            carver.msg(f"\n|R[WARD ALERT]|n Your Rune of Alarming on |w{target_entity.key}|n was tripped by |c{intruder.key}|n!\n")
        return True, "Alarm tripped."

    elif ward_type == "frost":
        curr_stam = getattr(intruder.db, "stamina", 100) or 100
        intruder.db.stamina = max(0, curr_stam - 25)
        intruder.msg(f"\n|C*CRACKLE!* Azure frost erupts beneath you! The Glyph of Frost Warding chills your flesh! (-25 Stamina)|n\n")
        ward["is_armed"] = False
        target_entity.db.active_ward = ward
        return True, "Frost ward detonated."

    elif ward_type == "explosive":
        curr_hp = getattr(intruder.db, "hp", 100) or 100
        intruder.db.hp = max(1, curr_hp - 35)
        intruder.msg(f"\n|R*BOOOOOM!* A blinding flash of orange fire blasts upward! The Explosive Fire Sigil explodes! (-35 HP)|n\n")
        ward["is_armed"] = False
        target_entity.db.active_ward = ward
        return True, "Explosive ward detonated."

    return False, "Unhandled ward."


def disarm_ward(caller, target_obj=None):
    """Carefully scratches out and defuses a protective ward."""
    target = target_obj if target_obj else caller.location
    if not target or not getattr(target.db, "active_ward", None):
        return False, f"There are no active runes or wards etched on {target.key if target else 'here'}."

    ward = target.db.active_ward
    ward_name = ward.get("name", "Rune")
    target.db.active_ward = None

    caller.msg(f"\n|WWith surgical precision, you sever the mana flow and scrape clean the {ward_name}! The ward is dismantled.|n\n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} carefully defuses a magical ward inscribed upon {target.key}.",
            exclude=[caller]
        )
    return True, "Ward disarmed."

