"""
Unit & Integration Tests for Eldoria World Importers

Tests:
1. CircleMUD / tbaMUD .wld parsing
2. Structured JSON area parsing
3. BFS 3D coordinate propagation for automapper telemetry
4. Dry-run graph validation
5. Live zone ingestion, entity instantiation, and reciprocal anchor linking
6. GMCP automapper telemetry on imported rooms
7. Zone purging / cleanup
"""

import os
import django
from django.conf import settings

# Initialize django if standalone test runner
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
    django.setup()

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.rooms import Room, get_gmcp_room_info
from world.importers import (
    parse_wld_file,
    parse_json_file,
    compute_relative_coordinates,
    validate_zone_data,
    import_zone,
    import_json,
    import_wld,
    purge_zone,
    find_room_by_key,
)


class TestZoneImporters(EvenniaTest):
    """Test suite for world importer parsers, builders, and GMCP telemetry."""

    def setUp(self):
        super().setUp()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "importers", "data")
        self.wld_path = os.path.join(self.data_dir, "sample_midgaard.wld")
        self.json_path = os.path.join(self.data_dir, "praxis_crypts.json")

    def test_wld_parser(self):
        """Verify CircleMUD / tbaMUD .wld parsing."""
        rooms = parse_wld_file(self.wld_path)
        self.assertIn(3001, rooms)
        self.assertIn(3002, rooms)
        self.assertIn(3003, rooms)
        self.assertIn(3004, rooms)
        self.assertIn(3005, rooms)

        r3001 = rooms[3001]
        self.assertEqual(r3001["name"], "The Temple of Midgaard")
        self.assertIn("grand Temple of Midgaard", r3001["desc"])
        self.assertIn("north", r3001["exits"])
        self.assertIn("south", r3001["exits"])
        self.assertEqual(r3001["exits"]["north"]["dest_vnum"], 3005)
        self.assertEqual(r3001["exits"]["south"]["dest_vnum"], 3002)

        # Room 3004 is sector 8 (underwater)
        r3004 = rooms[3004]
        self.assertEqual(r3004["terrain"], "underwater")
        self.assertEqual(r3004["exits"]["up"]["dest_vnum"], 3003)

    def test_json_parser(self):
        """Verify structured JSON area parsing."""
        data = parse_json_file(self.json_path)
        self.assertEqual(data["zone_key"], "praxis_crypts")
        self.assertEqual(data["zone_name"], "The Sunken Catacombs of Praxis")
        rooms = data["rooms"]
        self.assertIn("crypt_entrance", rooms)
        self.assertIn("crypt_hall", rooms)
        self.assertIn("crypt_sepulcher", rooms)
        self.assertIn("crypt_ossuary", rooms)
        self.assertIn("crypt_treasury", rooms)
        self.assertIn("crypt_shrine", rooms)

        # Check item and NPC definitions
        hall = rooms["crypt_hall"]
        self.assertEqual(len(hall["npcs"]), 1)
        self.assertEqual(hall["npcs"][0]["name"], "Barnacled Skeleton")

        entrance = rooms["crypt_entrance"]
        self.assertEqual(len(entrance["items"]), 1)
        self.assertEqual(entrance["items"][0]["name"], "Corroded Brass Lantern")

    def test_coordinate_propagation(self):
        """Verify BFS relative coordinate generation for automapping."""
        rooms = parse_wld_file(self.wld_path)
        coords = compute_relative_coordinates(rooms, start_id=3001, base_coords=(0, 0, 0))
        
        self.assertEqual(coords[3001], (0, 0, 0))
        # 3005 is north of 3001 -> y+1
        self.assertEqual(coords[3005], (0, 1, 0))
        # 3002 is south of 3001 -> y-1
        self.assertEqual(coords[3002], (0, -1, 0))
        # 3003 is east of 3002 -> (1, -1, 0)
        self.assertEqual(coords[3003], (1, -1, 0))
        # 3004 is down from 3003 -> (1, -1, -1)
        self.assertEqual(coords[3004], (1, -1, -1))

    def test_dry_run_validation(self):
        """Verify dry-run mode validates without creating database records."""
        data = parse_json_file(self.json_path)
        report = import_zone(data, dry_run=True)
        self.assertTrue(report["success"])
        self.assertEqual(report["rooms_created"], 6)

        # Confirm no database objects were actually created
        found = find_room_by_key("praxis_crypts_crypt_entrance")
        self.assertIsNone(found)

    def test_live_json_import_and_anchoring(self):
        """Verify live import, anchor exit creation, and GMCP telemetry."""
        # Create an anchor room in the world
        anchor_room = create_object(Room, key="Serpent Hollow Cavern")
        anchor_room.tags.add("isle_serpent_hollow", category="room_key")
        anchor_room.db.room_key = "isle_serpent_hollow"

        report = import_json(
            self.json_path,
            anchor_room_key="isle_serpent_hollow",
            anchor_exit_dir="down",
            return_exit_dir="up"
        )

        self.assertTrue(report["success"])
        self.assertEqual(report["rooms_created"], 6)
        self.assertEqual(report["npcs_created"], 2)
        self.assertEqual(report["items_created"], 4)
        self.assertEqual(report["anchored_to"], "Serpent Hollow Cavern")

        # Verify entrance room exists
        entrance = find_room_by_key("praxis_crypts_crypt_entrance")
        self.assertIsNotNone(entrance)
        self.assertEqual(entrance.key, "Flooded Archway to the Catacombs")

        # Verify reciprocal anchor exits
        exit_down = anchor_room.exits[0]
        self.assertEqual(exit_down.key, "down")
        self.assertEqual(exit_down.destination, entrance)

        exit_up = [ex for ex in entrance.exits if ex.key == "up"]
        self.assertTrue(len(exit_up) > 0)
        self.assertEqual(exit_up[0].destination, anchor_room)

        # Verify GMCP telemetry on imported room
        gmcp = get_gmcp_room_info(entrance)
        self.assertEqual(gmcp["zone"], "The Sunken Catacombs of Praxis")
        self.assertEqual(gmcp["terrain"], "catacombs")
        self.assertIn("n", gmcp["exits"])
        self.assertIn("d", gmcp["exits"])
        self.assertIn("u", gmcp["exits"])

        # Clean up zone via purge_zone
        purged_count = purge_zone("praxis_crypts")
        self.assertTrue(purged_count >= 6)
        self.assertIsNone(find_room_by_key("praxis_crypts_crypt_entrance"))

    def test_live_wld_import(self):
        """Verify live import of CircleMUD .wld file."""
        report = import_wld(
            self.wld_path,
            zone_key="midgaard_sample",
            zone_name="Midgaard Temple Square"
        )
        self.assertTrue(report["success"])
        self.assertEqual(report["rooms_created"], 5)

        r3001 = find_room_by_key("midgaard_sample_3001")
        self.assertIsNotNone(r3001)
        self.assertEqual(r3001.key, "The Temple of Midgaard")

        # Clean up
        purge_zone("midgaard_sample")
        self.assertIsNone(find_room_by_key("midgaard_sample_3001"))

