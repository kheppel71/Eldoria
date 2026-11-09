"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 7):
1. Renown Titles, Heroic Epithets & Accolades
2. Weapon Scabbards & Quick-Draw Sheathing
3. Dynamic World Boss Raids & Town Invasions
4. Gravedigging, Crypt Excavation & Relic Hunting
5. Wild Beekeeping, Honeycombs & Mead Fermentation
6. Hall of Champions & Realm Leaderboards
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_titles import (
    init_character_titles, unlock_title, set_active_title, get_full_titled_name
)
from world.nightmare_scabbards import (
    create_leather_scabbard, sheathe_weapon, draw_weapon
)
from world.nightmare_raids import (
    start_raid, end_raid, get_active_raids, format_raids_display, ACTIVE_RAIDS
)
from world.nightmare_gravedigging import (
    create_iron_shovel, is_excavation_site, perform_excavation
)
from world.nightmare_beekeeping import (
    create_wild_beehive, create_bee_smoker, smoke_hive, harvest_hive, brew_mead, craft_candle
)
from world.nightmare_leaderboards import (
    get_category_ranks, format_leaderboard_display
)


class TestNightmareSystemsPart7(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 7)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Praxis Ancient Cemetery")
        self.room.db.can_dig = True

        self.char1 = create_object(Character, key="Valerius", location=self.room)
        self.char2 = create_object(Character, key="Rowan", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.level = 15
        self.char1.db.coins = 500
        self.char1.db.bank_coins = 2000
        self.char1.db.arena_rating = 1450
        self.char1.db.quest_points = 85

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.level = 8
        self.char2.db.coins = 150
        self.char2.db.bank_coins = 300
        self.char2.db.arena_rating = 1100
        self.char2.db.quest_points = 20

        self.c1_msgs = []
        self.c2_msgs = []

        def capture_c1(msg=None, *args, **kwargs):
            if msg is not None:
                self.c1_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.c1_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        def capture_c2(msg=None, *args, **kwargs):
            if msg is not None:
                self.c2_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.c2_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        self.char1.msg = capture_c1
        self.char2.msg = capture_c2

    def tearDown(self):
        ACTIVE_RAIDS.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. RENOWN TITLES & HEROIC EPITHETS
    def test_titles_and_accolades(self):
        init_character_titles(self.char1)
        self.assertIn("None", self.char1.db.unlocked_prefixes)

        # Unlock prefix and epithet
        unlock_title(self.char1, "Sir", is_prefix=True)
        unlock_title(self.char1, "the Dragonslayer", is_prefix=False)

        self.assertIn("Sir", self.char1.db.unlocked_prefixes)
        self.assertIn("the Dragonslayer", self.char1.db.unlocked_epithets)

        # Set active prefix and epithet
        ok, msg = set_active_title(self.char1, "Sir")
        self.assertTrue(ok)
        ok, msg = set_active_title(self.char1, "Dragonslayer")
        self.assertTrue(ok)

        full_name = get_full_titled_name(self.char1)
        self.assertIn("Sir", full_name)
        self.assertIn("the Dragonslayer", full_name)

    # 2. WEAPON SCABBARDS & QUICK-DRAW
    def test_scabbards_and_quickdraw(self):
        scabbard = create_leather_scabbard(self.char1)
        sword = create_object(Object, key="Broadsword", location=self.char1)
        self.char1.db.equipped_slots = {"right_hand": sword}

        # Sheathe
        ok, msg = sheathe_weapon(self.char1, sword)
        self.assertTrue(ok)
        self.assertEqual(scabbard.db.sheathed_weapon, sword)
        self.assertIsNone(self.char1.db.equipped_slots.get("right_hand"))

        # Draw
        ok, msg = draw_weapon(self.char1)
        self.assertTrue(ok)
        self.assertIsNone(scabbard.db.sheathed_weapon)
        self.assertEqual(self.char1.db.equipped_slots.get("right_hand"), sword)

    # 3. WORLD BOSS RAIDS & TOWN INVASIONS
    def test_raids_and_invasions(self):
        ok, msg = start_raid("goblin_siege", room=self.room)
        self.assertTrue(ok)
        raids = get_active_raids()
        self.assertIn("goblin_siege", raids)

        display = format_raids_display()
        self.assertIn("Goblin Warlord Siege", display)

        # End raid with killer reward
        ok, msg = end_raid("goblin_siege", killer=self.char1)
        self.assertTrue(ok)
        self.assertNotIn("goblin_siege", get_active_raids())
        has_medal = any("Defender" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_medal)

    # 4. GRAVEDIGGING & CRYPT EXCAVATION
    def test_gravedigging_excavation(self):
        self.assertTrue(is_excavation_site(self.room))

        # Dig without shovel
        ok, msg = perform_excavation(self.char1)
        self.assertFalse(ok)

        # Dig with shovel
        shovel = create_iron_shovel(self.char1)
        ok, msg = perform_excavation(self.char1)
        self.assertTrue(ok)

    # 5. WILD BEEKEEPING & MEAD FERMENTATION
    def test_beekeeping_and_mead(self):
        hive = create_wild_beehive(self.room)
        smoker = create_bee_smoker(self.char1)

        # Harvest before pacifying -> stung by bees
        old_hp = self.char1.db.hp
        ok, msg = harvest_hive(self.char1)
        self.assertFalse(ok)
        self.assertLess(self.char1.db.hp, old_hp)

        # Smoke hive
        ok, msg = smoke_hive(self.char1)
        self.assertTrue(ok)
        self.assertTrue(hive.db.is_pacified)

        # Harvest pacified hive -> yields honeycomb and beeswax
        ok, msg = harvest_hive(self.char1)
        self.assertTrue(ok)
        has_comb = any("Honeycomb" in obj.key for obj in self.char1.contents)
        has_wax = any("Beeswax" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_comb)
        self.assertTrue(has_wax)

        # Brew mead
        ok, msg = brew_mead(self.char1)
        self.assertTrue(ok)
        has_mead = any("Mead" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_mead)

        # Craft candle
        ok, msg = craft_candle(self.char1)
        self.assertTrue(ok)
        has_candle = any("Candle" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_candle)

    # 6. HALL OF CHAMPIONS & REALM LEADERBOARDS
    def test_hall_of_champions_leaderboards(self):
        ranks = get_category_ranks("all")
        self.assertIn("gladiators", ranks)
        self.assertIn("questors", ranks)
        self.assertIn("wealth", ranks)
        self.assertIn("champions", ranks)

        board_text = format_leaderboard_display("all")
        self.assertIn("HALL OF CHAMPIONS", board_text)
        self.assertIn("GRAND GLADIATORS OF THE ARENA", board_text)

