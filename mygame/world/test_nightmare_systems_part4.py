"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 4):
1. Marriage, Spousal Rings & Telepathy
2. Tavern Intoxication & Drunken Slurs
3. Deities, Prayer & Sacrifices
4. Rune Inscriptions & Gem Socketing
5. Rogue Disguises & Scrutiny
6. Dungeon Hazards & Secret Passages
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_marriage import (
    propose_marriage, accept_proposal, divorce_spouse, ring_telepathy,
    ring_sense_spouse, PENDING_PROPOSALS
)
from world.nightmare_intoxication import consume_tavern_drink, apply_drunken_slur
from world.nightmare_deities import worship_deity, pray_at_altar, sacrifice_to_deity
from world.nightmare_enchanting import inscribe_weapon_with_rune, socket_gem_into_gear, RUNES, GEMS
from world.nightmare_disguise import create_disguise_kit, apply_disguise, remove_disguise, scrutinize_target
from world.nightmare_dungeon_secrets import search_dungeon_walls, disarm_dungeon_trap, push_secret_brick


class TestNightmareSystemsPart4(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 4)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Underworld Vault")
        self.room.db.terrain = "dungeon"

        self.char1 = create_object(Character, key="Rowan", location=self.room)
        self.char2 = create_object(Character, key="Lyra", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.mana = 100
        self.char1.db.max_mana = 100
        self.char1.db.coins = {"gold": 300, "silver": 50, "copper": 20}
        self.char1.db.dex = 40
        self.char1.db.wis = 30

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.coins = {"gold": 300, "silver": 50, "copper": 20}

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

        PENDING_PROPOSALS.clear()

    def tearDown(self):
        PENDING_PROPOSALS.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. MARRIAGE & SPOUSAL RINGS
    def test_marriage_system(self):
        # Propose
        ok, msg = propose_marriage(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertIn(self.char2.id, PENDING_PROPOSALS)

        # Accept
        ok, msg = accept_proposal(self.char2)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.spouse, self.char2.key)
        self.assertEqual(self.char2.db.spouse, self.char1.key)

        # Ring Telepathy & Sense
        ok, msg = ring_telepathy(self.char1, "Meet me by the fountain, beloved.")
        self.assertTrue(ok)

        ok, msg = ring_sense_spouse(self.char1)
        self.assertTrue(ok)

        # Divorce
        ok, msg = divorce_spouse(self.char1)
        self.assertTrue(ok)
        self.assertIsNone(self.char1.db.spouse)
        self.assertIsNone(self.char2.db.spouse)

    # 2. INTOXICATION & SLURS
    def test_intoxication_and_slurs(self):
        # Order stout
        ok, msg = consume_tavern_drink(self.char1, "stout")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.intoxication, 25)

        # Drink whiskey for liquid courage
        ok, msg = consume_tavern_drink(self.char1, "whiskey")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.intoxication, 70)
        self.assertTrue(self.char1.db.liquid_courage)

        # Drunken slur filter
        slurred = apply_drunken_slur("Stay back you shadowy thief", 70)
        self.assertIn("Shtay", slurred)

        # Sober up with coffee
        ok, msg = consume_tavern_drink(self.char1, "coffee")
        self.assertTrue(ok)
        self.assertLess(self.char1.db.intoxication, 70)

    # 3. DEITIES & DEVOTION
    def test_deities_and_prayer(self):
        ok, msg = worship_deity(self.char1, "solaris")
        self.assertTrue(ok)
        self.assertIn("Solaris", self.char1.db.deity)

        # Pray
        self.char1.db.hp = 50
        ok, msg = pray_at_altar(self.char1)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, 50)

        # Sacrifice
        ok, msg = sacrifice_to_deity(self.char1, 20)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.divine_favor, 10)

    # 4. ENCHANTING & SOCKETING
    def test_enchanting_and_socketing(self):
        weapon = create_object(Object, key="Mithril Rapier", location=self.char1)
        weapon.db.damage_bonus = 6
        weapon.db.slot = "right_hand"

        # Inscribe Rune
        rune = create_object(Object, key="Rune of Pyros", location=self.char1)
        ok, msg = inscribe_weapon_with_rune(self.char1, rune, weapon)
        self.assertTrue(ok)
        self.assertIsNotNone(weapon.db.rune_enchant)
        self.assertEqual(weapon.db.rune_enchant["element"], "Fire")

        # Socket Gem
        gem = create_object(Object, key="Cut Star Ruby", location=self.char1)
        ok, msg = socket_gem_into_gear(self.char1, gem, weapon)
        self.assertTrue(ok)
        self.assertIsNotNone(weapon.db.socketed_gem)

    # 5. DISGUISES & SCRUTINY
    def test_disguises_and_scrutiny(self):
        kit = create_disguise_kit(location=self.char1)
        ok, msg = apply_disguise(self.char1, "Old Beggar Jack", kit)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.is_disguised)
        self.assertEqual(self.char1.db.disguised_name, "Old Beggar Jack")

        # Scrutinize
        self.char2.db.wis = 50
        self.char1.db.dex = 5
        scrutinize_ok, _ = scrutinize_target(self.char2, self.char1)
        self.assertTrue(scrutinize_ok)
        self.assertFalse(self.char1.db.is_disguised)

    # 6. DUNGEON HAZARDS & SECRET PASSAGES
    def test_dungeon_secrets(self):
        # Configure room hazard and secret passage
        self.room.db.dungeon_hazard = {"type": "Poison Dart Trap", "diff": 20, "detected": False, "disarmed": False}
        self.room.db.secret_passage = {"revealed": False, "opened": False}

        # Search walls
        self.char1.db.wis = 50
        ok, msg = search_dungeon_walls(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.dungeon_hazard["detected"])
        self.assertTrue(self.room.db.secret_passage["revealed"])

        # Disarm trap
        self.char1.db.dex = 50
        ok, msg = disarm_dungeon_trap(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.dungeon_hazard["disarmed"])

        # Push secret brick
        ok, msg = push_secret_brick(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.secret_passage["opened"])

