"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 5):
1. Artifact Identification & Relic Lore
2. Cursed Equipment & Cleansing
3. Wilderness Camping & Campfires
4. Beast Taming & Animal Companions
5. Tavern Dice Gambling
6. Martial Specializations
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_identification import (
    create_unidentified_relic, identify_item, read_item_lore
)
from world.nightmare_curses import (
    create_cursed_item, equip_cursed_item, attempt_remove_cursed, uncurse_item
)
from world.nightmare_camping import (
    pitch_campsite_tent, light_campfire, strike_campsite
)
from world.nightmare_taming import (
    tame_wild_beast, order_companion, feed_companion
)
from world.nightmare_gambling import play_dice_hazard
from world.nightmare_specialization import choose_specialization, SPECIALIZATIONS


class TestNightmareSystemsPart5(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 5)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Whispering Wilderness Glade")
        self.room.db.terrain = "forest"

        self.char1 = create_object(Character, key="Ranger_Sylas", location=self.room)
        self.char2 = create_object(Character, key="Cleric_Althea", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.mana = 100
        self.char1.db.max_mana = 100
        self.char1.db.coins = {"gold": 300, "silver": 50, "copper": 20}
        self.char1.db.level = 6

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.mana = 100
        self.char2.db.max_mana = 100
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

    def tearDown(self):
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. IDENTIFICATION & LORE
    def test_identification_and_lore(self):
        relic = create_unidentified_relic(
            location=self.char1,
            true_name="Sunblade of Dawn",
            unidentified_name="Tarnished Rune Blade",
            lore_text="Forged in ancient solar fires to smite fiends.",
            damage_bonus=12
        )
        self.assertFalse(relic.db.is_identified)

        # Identify relic
        ok, msg = identify_item(self.char1, relic)
        self.assertTrue(ok)
        self.assertTrue(relic.db.is_identified)
        self.assertEqual(relic.key, "Sunblade of Dawn")

        # Read lore
        ok, msg = read_item_lore(self.char1, relic)
        self.assertTrue(ok)

    # 2. CURSES & PURIFICATION
    def test_curses_and_purification(self):
        cursed_sword = create_cursed_item(location=self.char1)
        self.assertTrue(cursed_sword.db.is_cursed)

        # Equip
        ok, msg = equip_cursed_item(self.char1, cursed_sword)
        self.assertTrue(ok)
        self.assertTrue(cursed_sword.db.is_bound)

        # Attempt to remove should fail
        can_remove = attempt_remove_cursed(self.char1, cursed_sword)
        self.assertFalse(can_remove)

        # Uncurse
        ok, msg = uncurse_item(self.char2, cursed_sword, target=self.char1)
        self.assertTrue(ok)
        self.assertFalse(cursed_sword.db.is_cursed)
        self.assertFalse(cursed_sword.db.is_bound)

    # 3. CAMPING & CAMPFIRES
    def test_camping_and_campfires(self):
        tent_kit = create_object(Object, key="Canvas Tent Kit", location=self.char1)

        # Pitch tent
        ok, msg = pitch_campsite_tent(self.char1, tent_kit)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.has_camp)

        # Light fire
        ok, msg = light_campfire(self.char1, None)
        self.assertTrue(ok)
        self.assertTrue(self.room.db.has_fire)

        # Strike camp
        ok, msg = strike_campsite(self.char1)
        self.assertTrue(ok)
        self.assertFalse(self.room.db.has_camp)
        self.assertFalse(self.room.db.has_fire)

    # 4. BEAST TAMING & COMPANIONS
    def test_beast_taming(self):
        wolf = create_object(Character, key="Wild Timber Wolf", location=self.room)
        wolf.db.is_beast = True
        meat = create_object(Object, key="Fresh Meat", location=self.char1)

        # Tame beast
        ok, msg = tame_wild_beast(self.char1, wolf, meat)
        self.assertTrue(ok)
        self.assertTrue(wolf.db.is_companion)
        self.assertEqual(self.char1.db.active_companion, wolf)

        # Order companion
        ok, msg = order_companion(self.char1, "stay")
        self.assertTrue(ok)

        # Feed companion
        extra_meat = create_object(Object, key="Cooked Meat", location=self.char1)
        ok, msg = feed_companion(self.char1, wolf, extra_meat)
        self.assertTrue(ok)

        # Release
        ok, msg = order_companion(self.char1, "release")
        self.assertTrue(ok)
        self.assertIsNone(self.char1.db.active_companion)
        wolf.delete()

    # 5. TAVERN GAMBLING
    def test_tavern_gambling(self):
        # Play dice hazard
        ok, msg = play_dice_hazard(self.char1, wager_gold=10)
        self.assertTrue(ok)

    # 6. MARTIAL SPECIALIZATION
    def test_specialization(self):
        ok, msg = choose_specialization(self.char1, "dualwield")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.specialization, "Dual-Wielding Mastery")

