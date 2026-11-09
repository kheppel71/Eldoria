"""
Unit tests for the Eldoria In-Game Mini-Map System and CmdMap
"""

import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
    django.setup()

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from world.minimap import render_minimap, get_minimap_panel
from commands.map_cmds import CmdMap


class TestMiniMapSystem(EvenniaTest):
    """Test suite verifying ASCII mini-map rendering and commands."""

    def setUp(self):
        super().setUp()
        # Create a 3-room test corridor: Room A <-> Room B <-> Room C
        self.room_a = create_object(Room, key="Western Orchard")
        self.room_a.db.terrain = "forest"
        self.room_a.db.coords = (-1, 0, 0)
        self.room_a.db.zone = "Test Realm"

        self.room_b = create_object(Room, key="Central Market")
        self.room_b.db.terrain = "city"
        self.room_b.db.coords = (0, 0, 0)
        self.room_b.db.zone = "Test Realm"

        self.room_c = create_object(Room, key="Eastern Mountains")
        self.room_c.db.terrain = "mountain"
        self.room_c.db.coords = (1, 0, 0)
        self.room_c.db.zone = "Test Realm"

        # Exits
        create_object(Exit, key="east", location=self.room_a, destination=self.room_b)
        create_object(Exit, key="west", location=self.room_b, destination=self.room_a)
        create_object(Exit, key="east", location=self.room_b, destination=self.room_c)
        create_object(Exit, key="west", location=self.room_c, destination=self.room_b)

        self.char1.location = self.room_b

    def test_minimap_rendering(self):
        """Verify that render_minimap correctly marks current position and connections."""
        ascii_map = render_minimap(self.room_b, radius=1)
        self.assertIn("@", ascii_map)
        # Western room is forest 'T', Eastern is mountain '^'
        self.assertIn("T", ascii_map)
        self.assertIn("^", ascii_map)
        self.assertIn("-", ascii_map)

    def test_minimap_panel(self):
        """Verify complete panel output with zone, coords, and terrain."""
        panel = get_minimap_panel(self.room_b, radius=1)
        self.assertIn("Central Market", panel)
        self.assertIn("Test Realm", panel)
        self.assertIn("Coords:", panel)
        self.assertIn("Legend:", panel)

    def test_cmd_map(self):
        """Test the 'map' command execution."""
        cmd = CmdMap()
        cmd.caller = self.char1

        # Standard map
        cmd.args = ""
        cmd.func()

        # Toggle auto-minimap
        cmd.args = "auto on"
        cmd.func()
        self.assertTrue(self.char1.db.auto_minimap)

        # Room appearance with auto-minimap enabled
        appearance = self.room_b.return_appearance(self.char1)
        self.assertIn("@", appearance)

        # Toggle auto off
        cmd.args = "auto off"
        cmd.func()
        self.assertFalse(self.char1.db.auto_minimap)

