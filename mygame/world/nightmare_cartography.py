"""
Nightmare LPmud Wilderness Cartography & Player Map Drawing Engine.

Implements:
1. Charting surveyed rooms and exits onto parchment maps ('drawmap').
2. Custom player landmark annotations ('landmark <note>').
3. Reading and sharing hand-drawn regional maps ('viewmap').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_blank_parchment(location):
    """Spawns a blank piece of cartographic parchment."""
    p = create_object(Object, key="Blank Vellum Parchment", location=location)
    p.db.desc = "A smooth sheet of treated calfskin vellum ready for ink, charcoal, or cartographic drawing."
    p.db.is_blank_parchment = True
    p.db.value = 10
    return p


def draw_room_map(caller, parchment_obj):
    """Surveys the current location and charts it onto the parchment."""
    loc = caller.location
    if not loc:
        return False, "You cannot chart the void."

    parchment_obj.delete()

    exits = [e.key for e in loc.exits] if loc.exits else ["none"]
    exit_str = ", ".join(exits)
    terrain = getattr(loc.db, "terrain", "city") or "city"

    map_item = create_object(Object, key=f"Parchment Map of {loc.key}", location=caller)
    map_item.db.is_map = True
    map_item.db.sector_name = loc.key
    map_item.db.terrain = terrain
    map_item.db.exits = exit_str
    map_item.db.landmarks = []
    map_item.db.cartographer = caller.key
    map_item.db.value = 35

    caller.msg(f"\n|Y[CARTOGRAPHY SURVEY]|n With careful charcoal strokes, you chart the topography of |w{loc.key}|n onto the vellum!")
    caller.msg(f"Surveyed Exits: |c{exit_str}|n   Terrain: |y{terrain.capitalize()}|n")
    caller.msg("To annotate custom points of interest: |wlandmark <note>|n\n")

    if loc:
        loc.msg_contents(
            f"{caller.key} charts the surrounding topography onto a vellum map with charcoal.",
            exclude=[caller]
        )
    return True, "Map drawn."


def annotate_map_landmark(caller, map_obj, landmark_text):
    """Adds a custom landmark annotation onto an existing hand-drawn map."""
    if not getattr(map_obj.db, "is_map", False):
        return False, f"{map_obj.key} is not a cartographic map!"

    landmarks = getattr(map_obj.db, "landmarks", []) or []
    landmarks.append(landmark_text.strip())
    map_obj.db.landmarks = landmarks

    caller.msg(f"|yYou ink a new landmark note onto {map_obj.key}: '|w{landmark_text.strip()}|y'.|n")
    return True, "Landmark added."


def view_drawn_map(caller, map_obj):
    """Displays the cartographic details of a hand-drawn map."""
    if not getattr(map_obj.db, "is_map", False):
        return False, f"{map_obj.key} is not a map."

    sector = getattr(map_obj.db, "sector_name", "Unknown Sector")
    terrain = getattr(map_obj.db, "terrain", "wilds")
    exits = getattr(map_obj.db, "exits", "none")
    carto = getattr(map_obj.db, "cartographer", "Unknown")
    landmarks = getattr(map_obj.db, "landmarks", []) or []

    caller.msg(f"\n|w===================== CARTOGRAPHIC SURVEY =====================|n")
    caller.msg(f"Charted Sector: |y{sector}|n    Cartographer: |c{carto}|n")
    caller.msg(f"Terrain:        |g{terrain.capitalize()}|n")
    caller.msg(f"Exits:          |w{exits}|n")

    if landmarks:
        caller.msg("\n|YAnnotated Landmarks & Secrets:|n")
        for lm in landmarks:
            caller.msg(f"  |Y[*] {lm}|n")
    else:
        caller.msg("\n|xNo custom landmarks recorded on this map yet.|n")

    caller.msg("|w" + "=" * 58 + "|n\n")
    return True, "Map viewed."

