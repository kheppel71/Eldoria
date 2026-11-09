"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 10):
1. Falconry, Hunting Birds & Aerial Reconnaissance
2. Glassblowing, Alchemical Phials & Stained Glass Artistry
3. Truffle Hunting, Sniffer Hounds & Culinary Feasts
4. Underworld Black Markets, Shadow Passwords & Smuggler Dens
5. Clockwork Tinkering, Wind-up Automatons & Mechanical Decoys
6. Thermal Bathhouses, Steam Vapor & Mineral Soaking
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object
from typeclasses.exits import Exit

from world.nightmare_falconry import (
    call_hunting_bird, scout_with_bird, hunt_quarry_with_bird, feed_hunting_bird
)
from world.nightmare_glassblowing import (
    gather_silica_quartz, blow_glass_item
)
from world.nightmare_truffles import (
    leash_truffle_hound, hunt_truffles_in_area, dig_up_truffle, cook_truffle_feast
)
from world.nightmare_blackmarket import (
    verify_shadow_password, format_blackmarket_display, purchase_contraband
)
from world.nightmare_tinkering import (
    craft_tinker_gadget, wind_clockwork_gadget, deploy_clockwork_decoy
)
from world.nightmare_bathhouse import (
    format_bathhouse_directory, soak_in_pool, wash_battle_grime
)


class TestNightmareSystemsPart10(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 10)."""

    def setUp(self):
        super().setUp()
        self.room1 = create_object(Room, key="Praxis High Meadow")
        self.room2 = create_object(Room, key="Ancient Forest Glade")

        # Exit between rooms
        self.exit_north = create_object(Exit, key="north", location=self.room1, destination=self.room2)

        self.char1 = create_object(Character, key="Ranger_Gawain", location=self.room1)
        self.char2 = create_object(Character, key="Scout_Lile", location=self.room2)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 80
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 70
        self.char1.db.max_stamina = 100
        self.char1.db.mana = 60
        self.char1.db.max_mana = 100
        self.char1.db.coins = 500

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100

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
        if self.exit_north.pk:
            self.exit_north.delete()
        if self.room1.pk:
            self.room1.delete()
        if self.room2.pk:
            self.room2.delete()
        super().tearDown()

    # 1. FALCONRY & RECONNAISSANCE
    def test_falconry_hunting(self):
        ok, msg = call_hunting_bird(self.char1, "falcon")
        self.assertTrue(ok)
        self.assertIsNotNone(self.char1.db.hunting_bird)

        # Scout adjacent room
        ok, msg = scout_with_bird(self.char1, "north")
        self.assertTrue(ok)
        self.assertIn("Ancient Forest Glade", msg)

        # Hunt quarry
        ok, msg = hunt_quarry_with_bird(self.char1)
        self.assertTrue(ok)
        has_meat = any("Poultry" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_meat)

        # Feed bird
        ok, msg = feed_hunting_bird(self.char1)
        self.assertTrue(ok)

    # 2. GLASSBLOWING & ALCHEMICAL PHIALS
    def test_glassblowing(self):
        ok, msg = gather_silica_quartz(self.char1)
        self.assertTrue(ok)
        has_sand = any(getattr(obj.db, "is_silica", False) for obj in self.char1.contents)
        self.assertTrue(has_sand)

        # Blow glass phial
        ok, msg = blow_glass_item(self.char1, "phial")
        self.assertTrue(ok)
        has_phial = any("Reinforced" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_phial)

    # 3. TRUFFLE HUNTING & FEASTS
    def test_truffles_and_feasting(self):
        ok, msg = leash_truffle_hound(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.has_truffle_hound)

        # Sniff truffles
        ok, msg = hunt_truffles_in_area(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.truffle_scent_found)

        # Dig truffle
        ok, msg = dig_up_truffle(self.char1)
        self.assertTrue(ok)
        has_truffle = any(getattr(obj.db, "is_truffle", False) for obj in self.char1.contents)
        self.assertTrue(has_truffle)

        # Cook feast
        old_hp = self.char1.db.hp
        ok, msg = cook_truffle_feast(self.char1)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, old_hp)
        self.assertTrue(self.char1.db.well_fed_buff)

    # 4. BLACK MARKET & SHADOW PASSWORDS
    def test_blackmarket_and_passwords(self):
        # Incorrect password
        ok, msg = verify_shadow_password(self.char1, "open sesame")
        self.assertFalse(ok)

        # Correct password
        ok, msg = verify_shadow_password(self.char1, "shadows keep no records")
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.has_blackmarket_clearance)

        disp = format_blackmarket_display(self.char1)
        self.assertIn("CONTRABAND BAZAAR", disp)

        # Purchase contraband
        ok, msg = purchase_contraband(self.char1, "pickset")
        self.assertTrue(ok)
        has_pick = any("Skeleton Pickset" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_pick)

    # 5. CLOCKWORK TINKERING & DECOYS
    def test_tinkering_and_decoys(self):
        ok, msg = craft_tinker_gadget(self.char1, "decoy")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, 460)

        # Wind gadget
        ok, msg = wind_clockwork_gadget(self.char1, "decoy")
        self.assertTrue(ok)

        # Deploy decoy
        ok, msg = deploy_clockwork_decoy(self.char1)
        self.assertTrue(ok)
        has_deployed = any(getattr(obj.db, "is_deployed", False) for obj in self.room1.contents)
        self.assertTrue(has_deployed)

    # 6. THERMAL BATHHOUSE & MINERAL SOAKING
    def test_bathhouse_and_soaking(self):
        disp = format_bathhouse_directory()
        self.assertIn("PRAXIS CIVIC BATHHOUSE", disp)

        # Soak in Caldarium
        old_hp = self.char1.db.hp
        ok, msg = soak_in_pool(self.char1, "caldarium")
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, old_hp)
        self.assertTrue(self.char1.db.rejuvenated_buff)

        # Soak in Steam
        old_mana = self.char1.db.mana
        ok, msg = soak_in_pool(self.char1, "steam")
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.mana, old_mana)

        # Wash grime
        ok, msg = wash_battle_grime(self.char1)
        self.assertTrue(ok)

