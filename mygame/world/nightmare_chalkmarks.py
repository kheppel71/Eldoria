"""
Nightmare LPmud Dungeon Chalk Markings & Wayfinding Glyphs Engine.

Implements:
1. Spelunker colored chalk sticks (white, charcoal, crimson).
2. Wall and floor wayfinding marks ('chalkmark <symbol> [note]'):
   - Arrow (Directional path)
   - Skull (Deadly danger / trap hazard)
   - Eye (Secret passage / hidden treasure)
   - Cross (Sanctuary / safe rest spot)
3. Reading room inscriptions ('readmarks').
4. Smudging and wiping marks clean ('clearchalk').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

CHALK_SYMBOLS = {
    "arrow": "|c---> [ARROW]|n Wayfinding Trail / Recommended Direction",
    "skull": "|r(X_X) [SKULL]|n Lethal Hazard / Trapped Area Ahead",
    "eye": "|y(o.o) [EYE]|n Concealed Secret / Hidden Doorway",
    "cross": "|g[+] [CROSS]|n Consecrated Sanctuary / Safe Haven"
}


def create_chalk_stick(location, color="White"):
    """Spawns a stick of spelunker's chalk."""
    chalk = create_object(Object, key=f"Stick of {color.title()} Chalk", location=location)
    chalk.db.is_chalk = True
    chalk.db.color = color.title()
    chalk.db.desc = f"A dense stick of {color.lower()} gypsum chalk for scrawling navigational marks on stone walls."
    return chalk


def inscribe_chalk_mark(caller, symbol="arrow", message=""):
    """Scrawls a wayfinding mark on the stone wall of the current room."""
    room = caller.location
    if not room:
        return False, "You cannot chalk in the void."

    # Check for chalk
    chalk = None
    for obj in caller.contents:
        if getattr(obj.db, "is_chalk", False) or "chalk" in obj.key.lower():
            chalk = obj
            break

    if not chalk:
        return False, "You need a Stick of Chalk in your pack to mark the walls! ('chalkmark <symbol> [msg]')"

    sym_clean = symbol.strip().lower()
    matched = next((k for k in CHALK_SYMBOLS if sym_clean in k), "arrow")

    mark_data = {
        "symbol": matched,
        "author": caller.key,
        "note": message.strip() if message else "Follow this trail.",
        "display": CHALK_SYMBOLS[matched]
    }

    marks = getattr(room.db, "chalk_marks", []) or []
    marks.append(mark_data)
    room.db.chalk_marks = marks

    caller.msg(
        f"\n|Y[CHALK MARK]|n You firmly scrape {chalk.key} against the stone wall,\n"
        f"drawing {CHALK_SYMBOLS[matched]}: |w\"{mark_data['note']}\"|n!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} scrawls a chalk navigational glyph onto the stone wall.",
            exclude=[caller]
        )
    return True, "Chalk mark inscribed."


def read_room_chalk_marks(caller):
    """Reads all chalk graffiti and symbols left on the room's walls."""
    room = caller.location
    if not room:
        return "No walls in the void."

    marks = getattr(room.db, "chalk_marks", []) or []
    if not marks:
        return "The stone walls here are bare and clean of any chalk markings."

    lines = [
        "|c" + "=" * 65 + "|n",
        f"|w               EXPLORER CHALK MARKS: {room.key.upper()} |n",
        "|c" + "=" * 65 + "|n"
    ]

    for idx, m in enumerate(marks, 1):
        lines.append(f" |Y[{idx}]|n {m['display']}")
        lines.append(f"     |wNote:|n \"{m['note']}\" (|yInscribed by {m['author']}|n)")
        lines.append("     " + "-" * 59)

    lines.append("|c" + "=" * 65 + "|n")
    return "\n".join(lines)


def wipe_chalk_marks(caller):
    """Smudges away all chalk markings in the room with a damp sleeve."""
    room = caller.location
    if not room or not getattr(room.db, "chalk_marks", None):
        return False, "There are no chalk marks here to wipe away."

    room.db.chalk_marks = []
    caller.msg("\n|yYou rub a damp sleeve against the stone wall, smudging the chalk marks into illegible dust.|n\n")
    if room:
        room.msg_contents(f"{caller.key} wipes the stone wall clean, erasing all chalk markings.", exclude=[caller])
    return True, "Chalk erased."

