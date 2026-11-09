"""
Automated Zone & Area Importer for Evennia / Eldoria MUD

Translates parsed MUD world formats (.wld, .zon, JSON) into Evennia
Room, Exit, Character, and Object entities with:
- Automated 3D coordinate layout for GMCP automappers
- Seamless two-way anchor linking to existing world rooms
- Dry-run validation
- Idempotent cleanup / re-import support
"""

from collections import deque
from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.characters import Character
from typeclasses.objects import Object
from .wld_parser import parse_wld_file, parse_wld_content
from .json_parser import parse_json_file, parse_json_content

TAG_WORLD = "eldoria_world"

DELTA_MAP = {
    "north": (0, 1, 0), "n": (0, 1, 0),
    "south": (0, -1, 0), "s": (0, -1, 0),
    "east": (1, 0, 0), "e": (1, 0, 0),
    "west": (-1, 0, 0), "w": (-1, 0, 0),
    "northeast": (1, 1, 0), "ne": (1, 1, 0),
    "northwest": (-1, 1, 0), "nw": (-1, 1, 0),
    "southeast": (1, -1, 0), "se": (1, -1, 0),
    "southwest": (-1, -1, 0), "sw": (-1, -1, 0),
    "up": (0, 0, 1), "u": (0, 0, 1),
    "down": (0, 0, -1), "d": (0, 0, -1),
}

OPPOSITE_DIR = {
    "north": "south", "south": "north",
    "east": "west", "west": "east",
    "northeast": "southwest", "southwest": "northeast",
    "northwest": "southeast", "southeast": "northwest",
    "up": "down", "down": "up"
}

STANDARD_ALIASES = {
    "north": ["n"], "south": ["s"],
    "east": ["e"], "west": ["w"],
    "northeast": ["ne"], "northwest": ["nw"],
    "southeast": ["se"], "southwest": ["sw"],
    "up": ["u"], "down": ["d"]
}


def compute_relative_coordinates(rooms, start_id=None, base_coords=(0, 0, 0)):
    """
    Computes 3D coordinates (x, y, z) for all rooms in a zone using BFS propagation
    if coordinates are not already defined.
    """
    coords_map = {}
    if not rooms:
        return coords_map

    # Preserve any pre-existing coords
    for r_id, r_data in rooms.items():
        if r_data.get("coords"):
            coords_map[r_id] = tuple(r_data["coords"])

    # Determine BFS starting room
    if not start_id or (start_id not in rooms and str(start_id) not in rooms):
        if coords_map:
            start_id = next(iter(coords_map.keys()))
        else:
            start_id = next(iter(rooms.keys()))

    if start_id not in coords_map:
        coords_map[start_id] = base_coords
        coords_map[str(start_id)] = base_coords

    queue = deque([start_id])
    visited = {start_id}

    while queue:
        curr_id = queue.popleft()
        curr_coords = coords_map[curr_id]
        room_data = rooms.get(curr_id) or rooms.get(str(curr_id))
        if not room_data:
            continue

        for dir_name, exit_info in room_data.get("exits", {}).items():
            dest_id = exit_info.get("dest_id") or exit_info.get("dest_vnum")
            dest_key = dest_id
            if dest_key not in rooms and str(dest_id) in rooms:
                dest_key = str(dest_id)
            elif dest_key not in rooms and isinstance(dest_id, str) and dest_id.isdigit() and int(dest_id) in rooms:
                dest_key = int(dest_id)

            if dest_key in rooms and dest_key not in coords_map and str(dest_key) not in coords_map:
                delta = DELTA_MAP.get(dir_name.lower(), (0, 0, 0))
                new_coords = (
                    curr_coords[0] + delta[0],
                    curr_coords[1] + delta[1],
                    curr_coords[2] + delta[2],
                )
                coords_map[dest_key] = new_coords
                coords_map[str(dest_key)] = new_coords
                queue.append(dest_key)
                visited.add(dest_key)

    # For any disconnected islands, place at offset
    offset_y = 10
    for r_id in rooms:
        if r_id not in coords_map and str(r_id) not in coords_map:
            c = (base_coords[0], base_coords[1] + offset_y, base_coords[2])
            coords_map[r_id] = c
            coords_map[str(r_id)] = c
            offset_y += 5

    return coords_map


def validate_zone_data(zone_dict):
    """
    Validates zone dictionary for internal consistency.
    Returns: (is_valid, list_of_warnings, list_of_errors)
    """
    warnings = []
    errors = []
    rooms = zone_dict.get("rooms", {})

    if not rooms:
        errors.append("Zone contains no rooms.")
        return False, warnings, errors

    all_ids = set(str(k) for k in rooms.keys())

    for r_id, r_data in rooms.items():
        for dir_name, exit_info in r_data.get("exits", {}).items():
            dest = str(exit_info.get("dest_id") or exit_info.get("dest_vnum", ""))
            if dest not in all_ids:
                warnings.append(f"Room '{r_id}' exit '{dir_name}' points to external/unknown destination '{dest}'.")

    return len(errors) == 0, warnings, errors


def find_room_by_key(key_or_vnum):
    """Locates an existing Evennia room by its room_key tag, db_key, or numeric ID."""
    # Try room_key category tag
    found = ObjectDB.objects.filter(db_tags__db_key=str(key_or_vnum), db_tags__db_category="room_key").first()
    if found:
        return found
    # Try exact db_key
    found = ObjectDB.objects.filter(db_key__iexact=str(key_or_vnum), db_typeclass_path__icontains="Room").first()
    if found:
        return found
    # Try numeric ID
    if str(key_or_vnum).isdigit():
        try:
            return ObjectDB.objects.get(id=int(key_or_vnum))
        except ObjectDB.DoesNotExist:
            pass
    return None


def purge_zone(zone_key):
    """
    Safely removes all rooms, exits, NPCs, and objects tagged with a given zone_key.
    Useful for cleanly re-importing updated zones.
    """
    tagged = list(ObjectDB.objects.filter(db_tags__db_key=str(zone_key), db_tags__db_category="zone").distinct())
    count = len(tagged)
    for obj in tagged:
        try:
            obj.delete()
        except Exception:
            pass
    return count


def import_zone(
    zone_data,
    anchor_room_key=None,
    anchor_exit_dir="down",
    return_exit_dir=None,
    anchor_zone_room_id=None,
    dry_run=False,
    base_coords=None
):
    """
    Main importer entry point.
    
    Args:
        zone_data (dict): Standardized parsed zone dictionary.
        anchor_room_key (str, optional): Key or tag of existing world room to connect with.
        anchor_exit_dir (str): Direction from anchor room to imported zone entrance (e.g. 'down').
        return_exit_dir (str, optional): Direction from imported zone back to anchor room (e.g. 'up').
        anchor_zone_room_id (str, optional): Which imported room serves as entrance (default: first room).
        dry_run (bool): If True, validates without creating database records.
        base_coords (tuple, optional): (x, y, z) base origin coordinate offset.
    
    Returns:
        dict: Summary report of imported rooms, exits, entities, and status.
    """
    report = {
        "zone_key": zone_data.get("zone_key", "unknown"),
        "zone_name": zone_data.get("zone_name", "Unknown Zone"),
        "rooms_created": 0,
        "exits_created": 0,
        "npcs_created": 0,
        "items_created": 0,
        "anchored_to": None,
        "warnings": [],
        "errors": [],
        "success": False
    }

    # 1. Validate
    is_valid, warnings, errors = validate_zone_data(zone_data)
    report["warnings"].extend(warnings)
    report["errors"].extend(errors)

    if not is_valid:
        return report

    rooms_dict = zone_data["rooms"]
    zone_key = zone_data["zone_key"]
    zone_name = zone_data["zone_name"]

    # 2. Determine Entrance Room
    if anchor_zone_room_id and str(anchor_zone_room_id) in rooms_dict:
        entrance_id = str(anchor_zone_room_id)
    else:
        entrance_id = str(next(iter(rooms_dict.keys())))

    # 3. Coordinate Resolution
    origin_coords = base_coords or zone_data.get("base_coords", (0, 0, 0))
    coords_map = compute_relative_coordinates(rooms_dict, start_id=entrance_id, base_coords=origin_coords)

    if dry_run:
        report["rooms_created"] = len(rooms_dict)
        report["success"] = True
        return report

    # 4. Create Evennia Rooms
    created_rooms = {}
    for r_id, r_info in rooms_dict.items():
        full_room_key = f"{zone_key}_{r_id}"
        room_title = r_info.get("name") or r_info.get("title", f"Room {r_id}")
        room_desc = r_info.get("desc", "You see nothing special.")
        terrain = r_info.get("terrain", zone_data.get("default_terrain", "indoors"))
        coords = coords_map.get(str(r_id), (0, 0, 0))

        # Instantiate Room
        room_obj = create_object(
            Room,
            key=room_title,
            tags=[TAG_WORLD]
        )
        room_obj.tags.add(full_room_key, category="room_key")
        room_obj.tags.add(zone_key, category="zone")
        room_obj.db.room_key = full_room_key
        room_obj.db.desc = room_desc.strip()
        room_obj.db.zone = zone_name
        room_obj.db.terrain = terrain
        room_obj.db.coords = coords

        created_rooms[str(r_id)] = room_obj
        report["rooms_created"] += 1

        # Create Items inside room
        for item_data in r_info.get("items", []):
            item_name = item_data.get("name", "An Object")
            item_desc = item_data.get("desc", "A nondescript item.")
            aliases = item_data.get("aliases", [])
            item_obj = create_object(
                Object,
                key=item_name,
                location=room_obj,
                aliases=aliases,
                tags=[TAG_WORLD]
            )
            item_obj.tags.add(zone_key, category="zone")
            item_obj.db.desc = item_desc.strip()
            report["items_created"] += 1

        # Create NPCs inside room
        for npc_data in r_info.get("npcs", []):
            npc_name = npc_data.get("name", "A Creature")
            npc_desc = npc_data.get("desc", "A mysterious inhabitant.")
            aliases = npc_data.get("aliases", [])
            npc_obj = create_object(
                Character,
                key=npc_name,
                location=room_obj,
                aliases=aliases,
                tags=[TAG_WORLD]
            )
            npc_obj.tags.add(zone_key, category="zone")
            npc_obj.db.desc = npc_desc.strip()
            report["npcs_created"] += 1

    # 5. Create Internal Exits
    for r_id, r_info in rooms_dict.items():
        src_room = created_rooms[str(r_id)]
        for dir_name, exit_info in r_info.get("exits", {}).items():
            dest_key = str(exit_info.get("dest_id") or exit_info.get("dest_vnum", ""))
            if dest_key in created_rooms:
                dest_room = created_rooms[dest_key]
                alias = exit_info.get("alias")
                aliases = [alias] if alias else STANDARD_ALIASES.get(dir_name.lower(), [])
                
                ex_obj = create_object(
                    Exit,
                    key=dir_name,
                    location=src_room,
                    destination=dest_room,
                    aliases=aliases,
                    tags=[TAG_WORLD]
                )
                ex_obj.tags.add(zone_key, category="zone")
                if exit_info.get("desc"):
                    ex_obj.db.desc = exit_info["desc"]
                report["exits_created"] += 1

    # 6. Anchor to Existing World (if requested)
    if anchor_room_key:
        anchor_room = find_room_by_key(anchor_room_key)
        if anchor_room and entrance_id in created_rooms:
            entrance_room = created_rooms[entrance_id]
            ret_dir = return_exit_dir or OPPOSITE_DIR.get(anchor_exit_dir.lower(), "out")

            # Outward exit from anchor room into zone entrance
            ex_in = create_object(
                Exit,
                key=anchor_exit_dir,
                location=anchor_room,
                destination=entrance_room,
                aliases=STANDARD_ALIASES.get(anchor_exit_dir.lower(), []),
                tags=[TAG_WORLD]
            )
            ex_in.tags.add(zone_key, category="zone")

            # Return exit from zone entrance back into anchor room
            ex_out = create_object(
                Exit,
                key=ret_dir,
                location=entrance_room,
                destination=anchor_room,
                aliases=STANDARD_ALIASES.get(ret_dir.lower(), []),
                tags=[TAG_WORLD]
            )
            ex_out.tags.add(zone_key, category="zone")

            report["anchored_to"] = anchor_room.key
            report["exits_created"] += 2
        else:
            report["warnings"].append(f"Anchor room '{anchor_room_key}' could not be found.")

    report["success"] = True
    return report


def import_wld(filepath, **kwargs):
    """Helper to parse and import a CircleMUD/tbaMUD .wld file directly."""
    wld_rooms = parse_wld_file(filepath)
    zone_key = kwargs.pop("zone_key", "circle_imported")
    zone_name = kwargs.pop("zone_name", "Imported MUD Zone")

    zone_data = {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "indoors",
        "rooms": wld_rooms
    }
    return import_zone(zone_data, **kwargs)


def import_json(filepath, **kwargs):
    """Helper to parse and import a JSON zone file directly."""
    zone_data = parse_json_file(filepath)
    # Allow overriding meta via kwargs
    if "zone_key" in kwargs:
        zone_data["zone_key"] = kwargs.pop("zone_key")
    if "zone_name" in kwargs:
        zone_data["zone_name"] = kwargs.pop("zone_name")
    return import_zone(zone_data, **kwargs)
