"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 6):
1. Socials & Feelings Soul Engine
2. Mineral Prospecting, Mining & Smelting
3. Spell Scribing & Magic Scrolls
4. Wilderness Cartography & Mapping
5. Player Mentoring & Novice Channel
6. Soul Shards & Ancestral Reincarnation
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_socials import execute_social, SOCIALS_TABLE
from world.nightmare_mining import prospect_room, mine_ore_deposit, smelt_ore_into_ingot, ORES
from world.nightmare_scribing import scribe_spell_scroll, read_magic_scroll
from world.nightmare_cartography import draw_room_map, annotate_map_landmark, view_drawn_map
from world.nightmare_mentoring import register_as_guide, broadcast_newbie_channel, establish_tutoring
from world.nightmare_reincarnation import perform_reincarnation, HERITAGE_TRAITS


class TestNightmareSystemsPart6(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 6)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Deep Iron Mines")
        self.room.db.terrain = "dungeon"

        self.char1 = create_object(Character, key="Thorgar", location=self.room)
        self.char2 = create_object(Character, key="Kip", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 100
        self.char1.db.max_stamina = 100
        self.char1.db.mana = 100
        self.char1.db.max_mana = 100
        self.char1.db.level = 10

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.level = 2

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
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. SOCIALS & FEELINGS
    def test_socials_system(self):
        # Directed social with adverb
        ok, msg = execute_social(self.char1, "nod", f"sagely at {self.char2.key}")
        self.assertTrue(ok)

        # Undirected social
        ok, msg = execute_social(self.char1, "bow")
        self.assertTrue(ok)

    # 2. MINING & SMELTING
    def test_mining_and_smelting(self):
        # Prospect
        ok, msg = prospect_room(self.char1)
        self.assertTrue(ok)
        self.assertIsNotNone(self.room.db.ore_deposit)

        # Mine ore
        pick = create_object(Object, key="Iron Miner's Pickaxe", location=self.char1)
        ok, msg = mine_ore_deposit(self.char1, pick)
        self.assertTrue(ok)

        ore = next((o for o in self.char1.contents if "Ore" in o.key), None)
        self.assertIsNotNone(ore)

        # Smelt ore
        ok, msg = smelt_ore_into_ingot(self.char1, ore)
        self.assertTrue(ok)
        ingot = next((o for o in self.char1.contents if "Ingot" in o.key or "Bar" in o.key), None)
        self.assertIsNotNone(ingot)

    # 3. SCROLL SCRIBING & READING
    def test_scribing_and_reading(self):
        parchment = create_object(Object, key="Blank Parchment", location=self.char1)

        # Scribe scroll
        ok, msg = scribe_spell_scroll(self.char1, "heal", parchment)
        self.assertTrue(ok)

        scroll = next((o for o in self.char1.contents if "Scroll of" in o.key), None)
        self.assertIsNotNone(scroll)

        # Read scroll
        self.char2.db.hp = 40
        ok, msg = read_magic_scroll(self.char2, scroll)
        self.assertTrue(ok)
        self.assertGreater(self.char2.db.hp, 40)

    # 4. CARTOGRAPHY
    def test_cartography_system(self):
        vellum = create_object(Object, key="Blank Vellum Parchment", location=self.char1)

        # Draw map
        ok, msg = draw_room_map(self.char1, vellum)
        self.assertTrue(ok)

        map_obj = next((o for o in self.char1.contents if "Map of" in o.key), None)
        self.assertIsNotNone(map_obj)

        # Annotate landmark
        ok, msg = annotate_map_landmark(self.char1, map_obj, "Deep Mithril Vein")
        self.assertTrue(ok)
        self.assertIn("Deep Mithril Vein", map_obj.db.landmarks)

        # View map
        ok, msg = view_drawn_map(self.char1, map_obj)
        self.assertTrue(ok)

    # 5. MENTORING & NOVICE CHANNEL
    def test_mentoring_system(self):
        # Register guide
        ok, msg = register_as_guide(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.is_guide)

        # Newbie channel
        ok, msg = broadcast_newbie_channel(self.char1, "Welcome to Sigil, adventurers!")
        self.assertTrue(ok)

        # Tutoring
        ok, msg = establish_tutoring(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.tutee_id, self.char2.id)

    # 6. SOUL SHARDS & REINCARNATION
    def test_reincarnation_system(self):
        ok, msg = perform_reincarnation(self.char1, "blade_prowess")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.level, 1)
        self.assertEqual(self.char1.db.soul_shards, 1)
        self.assertIn("Blade Prowess", self.char1.db.heritage_traits)

