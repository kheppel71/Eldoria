"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 13):
1. Underwater Diving Bells, Shipwreck Salvage & Sunken Doubloons
2. Venom Milking, Toxic Brewing & Universal Antidotes
3. Aviary Courier Pigeons, Message Canisters & Skymail
4. Artisan Woodcarving, Whittling & Musical Instrument Crafting
5. Guild War Banners, Heraldic Standards & Rallying Warhorns
6. Graveyard Séances, Spirit Mediums & Ouija Talking Boards
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_diving import (
    create_diving_gear, equip_diving_suit, dive_into_depths, salvage_seabed, pry_open_chest
)
from world.nightmare_venom import (
    milk_creature_venom, brew_antidote_serum, apply_antidote
)
from world.nightmare_pigeons import (
    format_aviary_directory, dispatch_courier_pigeon, read_pigeon_letter
)
from world.nightmare_woodcarving import (
    whittle_wooden_curio, carve_wooden_flute, carve_bardic_lute
)
from world.nightmare_banners import (
    create_guild_war_banner, plant_war_banner, uproot_war_banner, sound_rallying_warhorn
)
from world.nightmare_seance import (
    create_spirit_board, begin_seance, summon_spectral_spirit, question_spectral_ghost
)


class TestNightmareSystemsPart13(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 13)."""

    def setUp(self):
        super().setUp()
        self.coast = create_object(Room, key="Smuggler's Coast Lagoon")

        self.char1 = create_object(Character, key="Diver_Finn", location=self.coast)
        self.char2 = create_object(Character, key="Bard_Lyanna", location=self.coast)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 80
        self.char1.db.max_hp = 100
        self.char1.db.coins = 500

        self.char2.db.hp = 70
        self.char2.db.max_hp = 100
        self.char2.db.coins = 200

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
        if self.coast.pk:
            self.coast.delete()
        super().tearDown()

    # 1. DIVING & SHIPWRECK SALVAGE
    def test_diving_and_salvage(self):
        gear = create_diving_gear(self.char1)
        self.assertIn(gear, self.char1.contents)

        # Equip diving suit
        ok, msg = equip_diving_suit(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.is_diving_equipped)

        # Dive
        ok, msg = dive_into_depths(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.is_submerged)

        # Salvage seabed
        ok, msg = salvage_seabed(self.char1)
        self.assertTrue(ok)
        has_salvage = any(getattr(obj.db, "is_salvage", False) for obj in self.char1.contents)
        self.assertTrue(has_salvage)

        # Pry open chest
        chest = create_object(Object, key="Barnacle-Crusted Sea Chest", location=self.char1)
        chest.db.is_chest = True
        chest.db.is_pried = False
        chest.db.doubloons = 75

        old_coins = self.char1.db.coins
        ok, msg = pry_open_chest(self.char1)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, old_coins + 75)

    # 2. VENOM MILKING & ANTIDOTES
    def test_venom_and_antidotes(self):
        ok, msg = milk_creature_venom(self.char1, "viper")
        self.assertTrue(ok)
        has_venom = any(getattr(obj.db, "is_venom", False) for obj in self.char1.contents)
        self.assertTrue(has_venom)

        # Brew antidote
        ok, msg = brew_antidote_serum(self.char1)
        self.assertTrue(ok)
        has_antidote = any(getattr(obj.db, "is_antidote", False) for obj in self.char1.contents)
        self.assertTrue(has_antidote)

        # Apply antidote
        old_hp = self.char1.db.hp
        ok, msg = apply_antidote(self.char1)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, old_hp)

    # 3. COURIER PIGEONS & SKYMAIL
    def test_pigeons_and_skymail(self):
        dir_text = format_aviary_directory()
        self.assertIn("PRAXIS ROOFTOP AVIARY", dir_text)

        # Dispatch pigeon
        ok, msg = dispatch_courier_pigeon(self.char1, self.char2, "Meet at the docks at midnight.")
        self.assertTrue(ok)
        has_letter = any(getattr(obj.db, "is_letter", False) for obj in self.char2.contents)
        self.assertTrue(has_letter)

        # Read letter
        ok, msg = read_pigeon_letter(self.char2)
        self.assertTrue(ok)

    # 4. WOODCARVING & INSTRUMENTS
    def test_woodcarving_and_instruments(self):
        ok, msg = whittle_wooden_curio(self.char1, "pipe")
        self.assertTrue(ok)
        has_pipe = any("Pipe" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_pipe)

        # Carve flute
        ok, msg = carve_wooden_flute(self.char1)
        self.assertTrue(ok)
        has_flute = any("Flute" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_flute)

        # Carve lute
        ok, msg = carve_bardic_lute(self.char1)
        self.assertTrue(ok)
        has_lute = any("Lute" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_lute)

    # 5. GUILD WAR BANNERS & WARHORNS
    def test_guild_banners_and_warhorn(self):
        banner = create_guild_war_banner(self.char1, "Iron Vanguard")
        self.assertIn(banner, self.char1.contents)

        # Plant banner
        ok, msg = plant_war_banner(self.char1)
        self.assertTrue(ok)
        self.assertTrue(banner.db.is_planted)

        # Uproot banner
        ok, msg = uproot_war_banner(self.char1)
        self.assertTrue(ok)
        self.assertFalse(banner.db.is_planted)

        # Sound warhorn
        ok, msg = sound_rallying_warhorn(self.char1)
        self.assertTrue(ok)

    # 6. SÉANCES & SPIRIT BOARDS
    def test_seances_and_spirits(self):
        board = create_spirit_board(self.char1)
        self.assertIn(board, self.char1.contents)

        # Begin séance
        ok, msg = begin_seance(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.coast.db.active_seance)

        # Summon spirit
        ok, msg = summon_spectral_spirit(self.char1, "Ghost of Captain Morgan")
        self.assertTrue(ok)

        # Question ghost
        ok, msg = question_spectral_ghost(self.char1, "treasure")
        self.assertTrue(ok)

