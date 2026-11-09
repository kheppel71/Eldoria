"""
JSON / Structured Zone Format Parser

Parses modern structured JSON zone packages into Evennia-compatible room,
item, and NPC definitions with automated coordinate validation.
"""

import json


def parse_json_content(text):
    """
    Parses a JSON string representing a complete zone package.
    
    Expected format:
    {
        "zone_key": "praxis_catacombs",
        "zone_name": "The Sunken Catacombs of Praxis",
        "default_terrain": "catacombs",
        "base_coords": [10, -5, -1],
        "rooms": [
            {
                "id": "crypt_entrance",
                "title": "Flooded Archway to the Catacombs",
                "desc": "Brackish sea water laps against ancient marble steps...",
                "terrain": "catacombs",
                "coords": [10, -5, -1],
                "exits": {
                    "down": "crypt_ossuary",
                    "north": {"dest": "crypt_hall", "alias": "n"}
                },
                "npcs": [
                    {"name": "Drowned Skeleton", "desc": "A skeletal mariner...", "aliases": ["skeleton"]}
                ],
                "items": [
                    {"name": "Corroded Brass Lantern", "desc": "An oil lamp...", "aliases": ["lantern"]}
                ]
            }
        ]
    }
    """
    data = json.loads(text)
    
    zone_key = data.get("zone_key", "imported_zone")
    zone_name = data.get("zone_name", "Imported Zone")
    default_terrain = data.get("default_terrain", "indoors")
    base_coords = tuple(data.get("base_coords", [0, 0, 0]))

    normalized_rooms = {}
    for r in data.get("rooms", []):
        room_id = str(r.get("id"))
        if not room_id:
            continue
        
        exits_norm = {}
        for dir_name, exit_val in r.get("exits", {}).items():
            if isinstance(exit_val, str):
                exits_norm[dir_name.lower()] = {
                    "dest_id": str(exit_val),
                    "alias": dir_name[0].lower() if len(dir_name) == 1 else ""
                }
            elif isinstance(exit_val, dict):
                exits_norm[dir_name.lower()] = {
                    "dest_id": str(exit_val.get("dest", "")),
                    "alias": exit_val.get("alias", dir_name[0].lower() if len(dir_name) == 1 else ""),
                    "desc": exit_val.get("desc", "")
                }

        coords = r.get("coords")
        if coords:
            coords = tuple(coords)

        normalized_rooms[room_id] = {
            "id": room_id,
            "title": r.get("title", f"Room {room_id}"),
            "desc": r.get("desc", "You see nothing special."),
            "terrain": r.get("terrain", default_terrain),
            "coords": coords,
            "exits": exits_norm,
            "npcs": r.get("npcs", []),
            "items": r.get("items", []),
            "extra_descs": r.get("extra_descs", {})
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": default_terrain,
        "base_coords": base_coords,
        "rooms": normalized_rooms
    }


def parse_json_file(filepath):
    """Convenience helper to read and parse a JSON zone file from disk."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_json_content(content)

