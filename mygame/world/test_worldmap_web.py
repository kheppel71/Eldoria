"""
Unit & Integration Tests for Eldoria World Cartographer Web Suite.
Tests:
1. /admin/worldmap/ endpoint status code and template rendering.
2. /admin/worldmap/api/data/ endpoint JSON structure and diagnostics audit.
3. /admin/worldmap/api/live/ real-time player tracking endpoint.
"""

from django.test import Client
from evennia.utils.test_resources import EvenniaTest
from web.admin.views import world_map_data_api, world_map_live_api, build_world_map_data


class TestWorldMapWeb(EvenniaTest):
    """Verifies that the web cartographer and API endpoints function cleanly."""

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_world_map_view(self):
        """Test GET /admin/worldmap/ renders successfully."""
        response = self.client.get("/admin/worldmap/")
        self.assertEqual(response.status_code, 200)

    def test_world_map_data_api(self):
        """Test GET /admin/worldmap/api/data/ returns complete graph and audit telemetry."""
        response = self.client.get("/admin/worldmap/api/data/")
        self.assertEqual(response.status_code, 200)

        # Check content structure
        import json
        data = json.loads(response.content)
        self.assertIn("nodes", data)
        self.assertIn("links", data)
        self.assertIn("zones", data)
        self.assertIn("audit", data)
        self.assertIn("summary", data["audit"])
        self.assertGreaterEqual(data["audit"]["summary"]["total_rooms"], 1)

    def test_world_map_live_api(self):
        """Test GET /admin/worldmap/api/live/ returns active player roster."""
        response = self.client.get("/admin/worldmap/api/live/")
        self.assertEqual(response.status_code, 200)

        import json
        data = json.loads(response.content)
        self.assertIn("players", data)
        self.assertIn("timestamp", data)
        data = json.loads(response.content)
        self.assertIn("players", data)
        self.assertIn("timestamp", data)
