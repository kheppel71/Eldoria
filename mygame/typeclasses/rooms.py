"""
Room Typeclass with GMCP Automapper Integration & Machine-Readable Formatting

Features:
1. Native GMCP Room.Info Out-of-Band telemetry (Mudlet, TinTin++, CMUD)
2. Machine-parseable standardized exits line: [ Obvious exits: ... ]
3. Toggleable Automapper Mode (room IDs, zone, and coordinate tags)
4. Persistent Room-Key, Zone, and Terrain categorization
"""

from evennia.objects.objects import DefaultRoom
from .objects import ObjectParent


def get_gmcp_room_info(room):
    """
    Constructs a standard GMCP Room.Info payload for Mudlet and TinTin++ automappers.
    """
    if not room:
        return {}

    cardinal_map = {
        "north": "n", "south": "s", "east": "e", "west": "w",
        "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
        "up": "u", "down": "d",
        "n": "n", "s": "s", "e": "e", "w": "w",
        "ne": "ne", "nw": "nw", "se": "se", "sw": "sw",
        "u": "u", "d": "d"
    }

    exits_dict = {}
    for ex in room.exits:
        dest = ex.destination
        if dest:
            key_lower = ex.key.lower()
            short_dir = cardinal_map.get(key_lower, key_lower)
            exits_dict[short_dir] = dest.id

    zone_name = getattr(room.db, "zone", None) or "Eldoria"
    terrain_type = getattr(room.db, "terrain", None) or "indoors"
    coords = getattr(room.db, "coords", None)
    coord_dict = {"x": coords[0], "y": coords[1], "z": coords[2]} if coords else {"x": 0, "y": 0, "z": 0}

    return {
        "num": room.id,
        "name": room.key,
        "zone": zone_name,
        "terrain": terrain_type,
        "details": "",
        "exits": exits_dict,
        "coord": coord_dict
    }


def emit_gmcp_room_info(target, room):
    """
    Safely delivers GMCP Room.Info out-of-band telemetry only to client sessions
    that support and negotiated GMCP (e.g. Mudlet, TinTin++, cMUD).
    Prevents 'Error or Unhandled event' errors in non-GMCP clients such as Evennia's webclient.
    """
    if not target or not room:
        return
    sessions = getattr(target, "sessions", None)
    if not sessions:
        return
    active_sessions = sessions.all()
    if not active_sessions:
        return

    payload = None
    for sess in active_sessions:
        pflags = getattr(sess, "protocol_flags", {})
        # Only send if the session explicitly negotiated GMCP via Telnet subnegotiation
        # or has client-level GMCP enabled
        if pflags.get("GMCP", False) or pflags.get("gmcp", False):
            if payload is None:
                payload = get_gmcp_room_info(room)
            sess.msg(gmcp=("Room.Info", payload))


class Room(ObjectParent, DefaultRoom):
    """
    Enhanced Room typeclass providing:
    - GMCP Room.Info out-of-band updates on movement and look
    - Formatted, mapper-friendly room descriptions
    """

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """
        Triggered when any entity enters this room.
        Emits GMCP Room.Info to player clients immediately if GMCP is supported.
        """
        super().at_object_receive(moved_obj, source_location, **kwargs)
        if hasattr(moved_obj, "msg") and (moved_obj.has_account or getattr(moved_obj.db, "is_character", False)):
            emit_gmcp_room_info(moved_obj, self)

    def format_exits_line(self, looker):
        """
        Builds a clean, standardized, machine-parseable exits string.
        """
        if not self.exits:
            return "|x[ Obvious exits: none ]|n"

        exit_strings = []
        is_mapper = bool(getattr(looker.db, "mapper_mode", False))

        cardinals = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down"]

        for ex in self.exits:
            dest = ex.destination
            k = ex.key.lower()
            dest_tag = f"(#{dest.id})" if (is_mapper and dest) else ""

            if k in cardinals:
                exit_strings.append(f"|g{ex.key}|n{dest_tag}")
            else:
                exit_strings.append(f"|c[{ex.key}]|n{dest_tag}")

        return f"|w[ Obvious exits: {', '.join(exit_strings)} ]|n"

    def return_appearance(self, looker, **kwargs):
        """
        Formats room appearance with automapper metadata, standardized exits, and GMCP telemetry.
        """
        if not looker:
            return ""

        # Emit out-of-band GMCP Room.Info payload to GMCP-negotiated sessions
        emit_gmcp_room_info(looker, self)

        is_mapper = bool(getattr(looker.db, "mapper_mode", False))

        # Check darkness
        is_dark = getattr(self.db, "is_dark", False)
        from world.nightmare_core import room_is_illuminated
        illuminated = room_is_illuminated(looker, self)

        if is_dark and not illuminated:
            if is_mapper:
                return (
                    f"|w[#{self.id}] Pitch Black Darkness|n\n"
                    "It is pitch black; you cannot see your hand in front of your face.\n"
                    f"{self.format_exits_line(looker)}"
                )
            return (
                "|wPitch Black Darkness|n\n"
                "It is pitch black; you cannot see your hand in front of your face.\n"
                "You need a light source or nightvision to perceive your surroundings!"
            )

        # Header Title
        zone = getattr(self.db, "zone", "Eldoria")
        if is_mapper:
            title = f"|w[#{self.id}] |c{self.key}|n |x({zone})|n"
        else:
            title = f"|c{self.key}|n"

        # Room Description
        desc = self.db.desc or "You see nothing special."

        # Contents (Items and Characters)
        contents = self.contents
        items = []
        characters = []

        for obj in contents:
            if obj == looker:
                continue
            if obj.destination:
                # Exits are handled separately in exits line
                continue
            if obj.has_account or getattr(obj.db, "is_character", False):
                ghost_tag = " |r[GHOST]|n" if getattr(obj.db, "is_ghost", False) else ""
                characters.append(f"|y{obj.key}|n{ghost_tag} is standing here.")
            else:
                items.append(f"|w{obj.key}|n rests here.")

        # Construct final appearance
        sections = [title]

        # Check auto minimap
        if getattr(looker.db, "auto_minimap", False):
            from world.minimap import render_minimap
            mini = render_minimap(self, radius=1, caller=looker)
            if mini:
                sections.append(mini)

        sections.append(desc)

        if items:
            sections.append("\n".join(items))
        if characters:
            sections.append("\n".join(characters))

        # Standardized exits line
        sections.append(self.format_exits_line(looker))

        if is_mapper:
            exits_summary = ", ".join([f"{ex.key}->#{ex.destination.id}" for ex in self.exits if ex.destination])
            sections.append(f"|x[ Telemetry | ID: #{self.id} | Zone: {zone} | Routes: {exits_summary} ]|n")

        return "\n\n".join(sections)
