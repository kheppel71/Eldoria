"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 3):
1. Finger, Plan & Immortal Suite
2. Wilderness Fishing & Angling
3. Hunting Traps & Caltrops
4. Grand Arena Duels & Wagers
5. Bardic Instruments & War Songs
6. Trophy Taxidermy & Wall Mounts
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_finger_immortal import (
    get_finger_data, set_player_plan, toggle_invis, teleport_to, summon_player
)
from world.nightmare_fishing import (
    attach_bait_to_rod, cast_fishing_line, reel_fishing_line
)
from world.nightmare_traps import (
    set_room_trap, spring_room_traps, scatter_caltrops
)
from world.nightmare_arena import (
    challenge_duel, accept_duel, conclude_duel, PENDING_DUELS
)
from world.nightmare_bard import (
    play_instrument, sing_bardic_song
)
from world.nightmare_trophies import (
    craft_taxidermy_trophy, mount_trophy_on_wall
)


class TestNightmareSystemsPart3(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 3)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Grand Harbor Docks")
        self.room.db.terrain = "coast"

        self.char1 = create_object(Character, key="Aethelgard", location=self.room)
        self.char2 = create_object(Character, key="Vespera", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 100
        self.char1.db.max_stamina = 100
        self.char1.db.dex = 30
        self.char1.db.coins = {"gold": 200, "silver": 50, "copper": 20}

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.stamina = 100
        self.char2.db.max_stamina = 100
        self.char2.db.dex = 30
        self.char2.db.coins = {"gold": 200, "silver": 50, "copper": 20}

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

        PENDING_DUELS.clear()

    def tearDown(self):
        PENDING_DUELS.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. FINGER & IMMORTAL SUITE
    def test_finger_and_immortal(self):
        set_player_plan(self.char1, "To seek glory in the Great Beyond.")
        self.assertEqual(self.char1.db.plan, "To seek glory in the Great Beyond.")

        dossier = get_finger_data(self.char1)
        self.assertIn("Aethelgard", dossier)
        self.assertIn("To seek glory", dossier)

        # Invisibility toggle
        is_inv = toggle_invis(self.char1)
        self.assertTrue(is_inv)
        is_inv2 = toggle_invis(self.char1)
        self.assertFalse(is_inv2)

        # Teleport and Summon
        dest_room = create_object(Room, key="Archmage Sanctum")
        ok, msg = teleport_to(self.char1, dest_room)
        self.assertTrue(ok)
        self.assertEqual(self.char1.location, dest_room)

        ok, msg = summon_player(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertEqual(self.char2.location, dest_room)
        dest_room.delete()

    # 2. FISHING & ANGLING
    def test_fishing_system(self):
        rod = create_object(Object, key="Ashwood Fishing Rod", location=self.char1)
        bait = create_object(Object, key="Juicy Earthworm Bait", location=self.char1)

        # Attach bait
        ok, msg = attach_bait_to_rod(self.char1, bait, rod)
        self.assertTrue(ok)
        self.assertTrue(rod.db.has_bait)

        # Cast line
        ok, msg = cast_fishing_line(self.char1, rod)
        self.assertTrue(ok)
        self.assertTrue(self.char1.ndb.is_fishing)

        # Reel in
        self.char1.db.dex = 80
        ok, msg = reel_fishing_line(self.char1)
        self.assertTrue(ok)
        self.assertFalse(self.char1.ndb.is_fishing)

    # 3. TRAPS & CALTROPS
    def test_traps_and_caltrops(self):
        trap_kit = create_object(Object, key="Iron Bear Trap Kit", location=self.char1)
        ok, msg = set_room_trap(self.char1, "beartrap", trap_kit)
        self.assertTrue(ok)
        self.assertTrue(bool(self.room.db.room_traps))

        # Step into trap
        spring_ok = spring_room_traps(self.char2, self.room)
        self.assertTrue(spring_ok)
        self.assertLess(self.char2.db.hp, 100)

        # Caltrops
        caltrop_bag = create_object(Object, key="Bag of Caltrops", location=self.char1)
        ok, msg = scatter_caltrops(self.char1, caltrop_bag)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.has_caltrops)

    # 4. GRAND ARENA DUELS
    def test_arena_duels(self):
        # Challenge duel
        ok, msg = challenge_duel(self.char1, self.char2, wager=25)
        self.assertTrue(ok)
        self.assertIn(self.char2.id, PENDING_DUELS)

        # Accept duel
        ok, msg = accept_duel(self.char2)
        self.assertTrue(ok)
        self.assertEqual(self.char1.location, self.char2.location)
        self.assertTrue(getattr(self.char1.location.db, "is_arena", False))

        # Conclude duel
        ok, msg = conclude_duel(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.coins["gold"], 200)
        self.assertLess(self.char2.db.coins["gold"], 200)

    # 5. BARDIC PERFORMANCE
    def test_bardic_performance(self):
        lute = create_object(Object, key="Ornate Gilded Lute", location=self.char1)
        ok, msg = play_instrument(self.char1, lute)
        self.assertTrue(ok)

        # Sing song
        self.char1.db.stamina = 50
        self.char1.db.hp = 50
        ok, msg = sing_bardic_song(self.char1, "vitality")
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, 50)

    # 6. TROPHY TAXIDERMY & MOUNTS
    def test_trophy_taxidermy(self):
        wolf_head = create_object(Object, key="Dire Wolf Head", location=self.char1)
        ok, msg = craft_taxidermy_trophy(self.char1, wolf_head)
        self.assertTrue(ok)

        trophy = next((o for o in self.char1.contents if "Trophy" in o.key), None)
        self.assertIsNotNone(trophy)

        # Mount trophy on wall
        ok, msg = mount_trophy_on_wall(self.char1, trophy)
        self.assertTrue(ok)
        self.assertEqual(len(self.room.db.wall_trophies), 1)

