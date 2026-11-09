"""
CircleMUD / tbaMUD / DikuMUD .wld (World) Format Parser

Parses classic ASCII .wld files into structured Python dictionary models
compatible with Evennia rooms, exits, and terrain systems.
"""

import re

# Mapping of classic Diku/Circle sector types to Eldoria terrain types
SECTOR_MAP = {
    0: "indoors",      # Inside
    1: "city",         # City
    2: "field",        # Field / Plains
    3: "forest",       # Forest
    4: "hills",        # Hills
    5: "mountain",     # Mountain
    6: "water_swim",   # Shallow Water
    7: "water_noswim", # Deep Water / Ocean
    8: "underwater",   # Underwater
    9: "air",          # Air / Flight
}

DIRECTION_MAP = {
    0: ("north", "n", (0, 1, 0)),
    1: ("east", "e", (1, 0, 0)),
    2: ("south", "s", (0, -1, 0)),
    3: ("west", "w", (-1, 0, 0)),
    4: ("up", "u", (0, 0, 1)),
    5: ("down", "d", (0, 0, -1)),
}


def parse_wld_content(text):
    """
    Parses the raw text of a .wld file and returns a dictionary of room structures:
    {
        vnum: {
            "vnum": int,
            "name": str,
            "desc": str,
            "sector": int,
            "terrain": str,
            "room_flags": int,
            "zone_num": int,
            "exits": {
                "north": {"dest_vnum": int, "alias": "n", "offset": (0, 1, 0), "door_flags": int},
                ...
            },
            "extra_descs": { "keyword": "desc" }
        }
    }
    """
    rooms = {}
    lines = text.splitlines()
    idx = 0
    total_lines = len(lines)

    def next_line():
        nonlocal idx
        if idx < total_lines:
            line = lines[idx]
            idx += 1
            return line
        return None

    def read_until_tilde(initial=""):
        nonlocal idx
        parts = [initial] if initial else []
        while idx < total_lines:
            line = lines[idx]
            idx += 1
            if "~" in line:
                before_tilde, _, _ = line.partition("~")
                parts.append(before_tilde)
                break
            parts.append(line)
        return "\n".join(parts).strip()

    while idx < total_lines:
        line = lines[idx].strip()
        idx += 1

        if not line or line.startswith("*"):
            continue

        if line == "$" or line == "$~":
            break

        if line.startswith("#"):
            try:
                vnum = int(line[1:].strip())
            except ValueError:
                continue

            # Read Room Name (ends with ~)
            name_raw = next_line() or ""
            if "~" in name_raw:
                name = name_raw.split("~")[0].strip()
            else:
                name = read_until_tilde(name_raw)

            # Read Room Description (multi-line, ends with ~)
            desc = read_until_tilde()

            # Read flags: <zone_num> <room_flags> <sector_type>
            flags_line = next_line() or "0 0 0"
            flag_tokens = flags_line.strip().split()
            zone_num = int(flag_tokens[0]) if len(flag_tokens) > 0 and flag_tokens[0].isdigit() else 0
            room_flags = int(flag_tokens[1]) if len(flag_tokens) > 1 and flag_tokens[1].isdigit() else 0
            sector = int(flag_tokens[2]) if len(flag_tokens) > 2 and flag_tokens[2].isdigit() else 0
            terrain = SECTOR_MAP.get(sector, "indoors")

            room_data = {
                "vnum": vnum,
                "name": name,
                "desc": desc,
                "zone_num": zone_num,
                "room_flags": room_flags,
                "sector": sector,
                "terrain": terrain,
                "exits": {},
                "extra_descs": {}
            }

            # Parse exits and extras until 'S' (or EOF)
            while idx < total_lines:
                curr = lines[idx].strip()
                if curr == "S":
                    idx += 1
                    break
                if curr.startswith("#") or curr == "$":
                    # Reached next room without 'S'
                    break

                idx += 1

                # Exit directive D0..D5
                if curr.startswith("D") and len(curr) >= 2 and curr[1].isdigit():
                    dir_num = int(curr[1])
                    if dir_num in DIRECTION_MAP:
                        dir_name, dir_alias, offset = DIRECTION_MAP[dir_num]
                        # Read exit description
                        _ = read_until_tilde()
                        # Read door keywords
                        door_kw = read_until_tilde()
                        # Read door flags: <flags> <key_vnum> <dest_vnum>
                        door_line = next_line() or "0 -1 -1"
                        door_tokens = door_line.strip().split()
                        try:
                            door_flags = int(door_tokens[0]) if len(door_tokens) > 0 else 0
                            dest_vnum = int(door_tokens[2]) if len(door_tokens) > 2 else -1
                        except ValueError:
                            door_flags, dest_vnum = 0, -1

                        if dest_vnum > 0:
                            room_data["exits"][dir_name] = {
                                "dest_vnum": dest_vnum,
                                "alias": dir_alias,
                                "offset": offset,
                                "door_flags": door_flags,
                                "door_kw": door_kw
                            }

                # Extra description directive E
                elif curr == "E":
                    kw_line = read_until_tilde()
                    extra_desc = read_until_tilde()
                    room_data["extra_descs"][kw_line] = extra_desc

            rooms[vnum] = room_data

    return rooms


def parse_wld_file(filepath):
    """Convenience helper to read and parse a .wld file from disk."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return parse_wld_content(content)
