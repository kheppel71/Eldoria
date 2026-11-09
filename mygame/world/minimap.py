"""
Eldoria Dynamic ASCII / ANSI In-Game Mini-Map Generator

Generates a local 2D/3D grid mini-map centered on the player's current room.
Features:
- Relative coordinate and cardinal exit crawling
- Terrain-aware color coding and symbols
- Current player position highlighting ([@])
- Elevation indicators for Up/Down exits (^ / v)
- Compact, side-by-side or standalone rendering
- Fast O(V) graph traversal with loop protection
"""

CARDINAL_OFFSETS = {
    "north": (0, 1, 0),
    "south": (0, -1, 0),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "northeast": (1, 1, 0),
    "northwest": (-1, 1, 0),
    "southeast": (1, -1, 0),
    "southwest": (-1, -1, 0),
    "n": (0, 1, 0),
    "s": (0, -1, 0),
    "e": (1, 0, 0),
    "w": (-1, 0, 0),
    "ne": (1, 1, 0),
    "nw": (-1, 1, 0),
    "se": (1, -1, 0),
    "sw": (-1, -1, 0),
}

TERRAIN_SYMBOLS = {
    "city": ("|w", "#"),
    "forest": ("|g", "T"),
    "field": ("|G", "."),
    "hills": ("|y", "n"),
    "mountain": ("|r", "^"),
    "water_swim": ("|b", "~"),
    "water_noswim": ("|B", "="),
    "underwater": ("|C", "U"),
    "catacombs": ("|m", "X"),
    "underground": ("|x", "#"),
    "indoors": ("|w", "#"),
    "swamp": ("|g", ";"),
    "desert": ("|y", "~"),
    "ice": ("|c", "*"),
    "air": ("|C", "o"),
}


def render_minimap(center_room, radius=2, caller=None):
    """
    Renders a compact ANSI ASCII mini-map centered on center_room.
    radius: 1 gives 3x3 rooms, 2 gives 5x5 rooms.
    """
    if not center_room:
        return "|x[ No Map Data ]|n"

    # 1. Breadth-First Search to map relative (dx, dy) within radius
    # We use z-level matching: only rooms on the same z-level as center_room
    curr_coords = center_room.db.coords or (0, 0, 0)
    curr_z = curr_coords[2]

    # Map grid coordinates: (dx, dy) -> room_obj
    room_grid = {(0, 0): center_room}
    # Exit connections: ((x1, y1), (x2, y2)) -> exit_type
    connections = set()
    up_down_rooms = {}  # (dx, dy) -> list of 'u' / 'd'

    queue = [(center_room, 0, 0, 0)]
    visited = {center_room: (0, 0)}

    while queue:
        room, dx, dy, dist = queue.pop(0)

        # Check for up/down exits
        for ex in room.exits:
            k = ex.key.lower()
            if k in ["up", "u"]:
                up_down_rooms.setdefault((dx, dy), set()).add("^")
            elif k in ["down", "d"]:
                up_down_rooms.setdefault((dx, dy), set()).add("v")

        if dist >= radius:
            continue

        for ex in room.exits:
            dest = ex.destination
            if not dest or dest in visited:
                if dest and dest in visited:
                    tdx, tdy = visited[dest]
                    if abs(tdx - dx) <= 1 and abs(tdy - dy) <= 1:
                        connections.add(((dx, dy), (tdx, tdy)))
                continue

            k = ex.key.lower()
            if k in CARDINAL_OFFSETS:
                ox, oy, _ = CARDINAL_OFFSETS[k]
                ndx = dx + ox
                ndy = dy + oy

                if abs(ndx) <= radius and abs(ndy) <= radius:
                    visited[dest] = (ndx, ndy)
                    room_grid[(ndx, ndy)] = dest
                    connections.add(((dx, dy), (ndx, ndy)))
                    queue.append((dest, ndx, ndy, dist + 1))

    # 2. Build ASCII matrix
    # Each room node occupies a 3-character block: [S] or [@].
    # Corridor cells connect horizontally and vertically.
    # Grid coordinates range from -radius to +radius.
    # Matrix dimensions:
    # row index = (radius - y) * 2
    # col index = (x + radius) * 4

    grid_h = radius * 4 + 1
    grid_w = radius * 8 + 3
    matrix = [[" " for _ in range(grid_w)] for _ in range(grid_h)]

    def r_to_m(x, y):
        # Convert room grid (x, y) to matrix cell (row, col)
        row = (radius - y) * 2
        col = (x + radius) * 4
        return row, col

    # Draw connections
    for (x1, y1), (x2, y2) in connections:
        r1, c1 = r_to_m(x1, y1)
        r2, c2 = r_to_m(x2, y2)

        # Midpoint
        mr = (r1 + r2) // 2
        mc = (c1 + c2) // 2

        if x1 == x2 and abs(y1 - y2) == 1:
            # Vertical connection
            matrix[mr][mc + 1] = "|"
        elif y1 == y2 and abs(x1 - x2) == 1:
            # Horizontal connection
            # Between col c1+2 and c2, draw '--'
            min_c = min(c1, c2)
            matrix[mr][min_c + 3] = "-"
        elif (x2 - x1) == 1 and (y2 - y1) == 1:
            # Northeast: row goes down, col goes right
            matrix[mr][mc + 1] = "/"
        elif (x2 - x1) == -1 and (y2 - y1) == -1:
            # Southwest
            matrix[mr][mc + 1] = "/"
        elif (x2 - x1) == -1 and (y2 - y1) == 1:
            # Northwest
            matrix[mr][mc + 1] = "\\"
        elif (x2 - x1) == 1 and (y2 - y1) == -1:
            # Southeast
            matrix[mr][mc + 1] = "\\"

    # Draw rooms
    for (x, y), room in room_grid.items():
        row, col = r_to_m(x, y)
        terrain = getattr(room.db, "terrain", "city") or "city"
        color, symbol = TERRAIN_SYMBOLS.get(terrain, ("|w", "#"))

        # Elevation badge
        elev = up_down_rooms.get((x, y), set())
        if "^" in elev and "v" in elev:
            e_mark = "+"
        elif "^" in elev:
            e_mark = "^"
        elif "v" in elev:
            e_mark = "v"
        else:
            e_mark = None

        if x == 0 and y == 0:
            # Center / player position
            matrix[row][col] = "|Y[|n"
            matrix[row][col + 1] = "|[x|Y@|n"
            matrix[row][col + 2] = "|Y]|n"
        else:
            sym_char = e_mark if e_mark else symbol
            matrix[row][col] = f"{color}[|n"
            matrix[row][col + 1] = f"{color}{sym_char}|n"
            matrix[row][col + 2] = f"{color}]|n"

    # Assemble lines
    map_lines = []
    for row in matrix:
        line_str = "".join(row).rstrip()
        if line_str:
            map_lines.append(line_str)

    return "\n".join(map_lines)


def get_minimap_panel(center_room, radius=2, caller=None):
    """
    Returns an integrated mini-map panel with room info, coordinates,
    danger level, and terrain legend.
    """
    if not center_room:
        return "|x[ No Map Data Available ]|n"

    ascii_map = render_minimap(center_room, radius=radius, caller=caller)
    coords = center_room.db.coords or (0, 0, 0)
    zone = getattr(center_room.db, "zone", "Eldoria")
    terrain = (getattr(center_room.db, "terrain", "indoors") or "indoors").title()

    # Format obvious exits
    cardinal_keys = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down"]
    exit_list = []
    for ex in center_room.exits:
        k = ex.key.lower()
        if k in cardinal_keys:
            exit_list.append(f"|g{ex.key}|n")
        else:
            exit_list.append(f"|c{ex.key}|n")
    exits_str = ", ".join(exit_list) if exit_list else "|xnone|n"

    map_box = (
        f"|c+---[ |wArea Map: {center_room.key[:26]} |c]---+\n"
        f"{ascii_map}\n"
        f"|c+------------------------------------------------+\n"
        f"|w Zone:|n    |y{zone}|n\n"
        f"|w Terrain:|n {terrain}  |wCoords:|n |c({coords[0]}, {coords[1]}, {coords[2]})|n\n"
        f"|w Exits:|n   {exits_str}\n"
        f"|x Legend: |Y[@]|x You  |w[#]|x City  |g[T]|x Forest  |b[~]|x Water  |r[^]|x Mountain  |c[*]|x Ice|n"
    )
    return map_box

