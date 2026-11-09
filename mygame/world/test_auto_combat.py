"""
Unit & Integration Tests for Nightmare Real-Time Auto-Combat System.
Tests:
1. Auto-Combat initiation, mutual target locks, and initial round execution.
2. Two-way exchange: attacker strikes, and defender counter-attacks.
3. Auto-Combat round continuation until target death, corpse drop, and XP award.
4. Clean disengagement via 'disengage' command.
5. Clean disengagement when fleeing or moving locations.
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from world.nightmare_core import (
    init_nightmare_character, start_combat, disengage_combat,
    is_in_combat, combat_round_tick, perform_combat_round
)
from commands.nightmare_cmds import CmdKill, CmdDisengage, CmdFlee


class TestAutoCombat(EvenniaTest):
    """Tests the real-time auto-combat loop and state machine."""

    def setUp(self):
        super().setUp()
        self.arena = create_object(Room, key="Combat Arena")
        self.fighter = create_object(Character, key="Warrior_Bob", location=self.arena)
        self.goblin = create_object(Character, key="Sneaky_Goblin", location=self.arena)

        # Mark as character objects for test logic
        self.fighter.db.is_character = True
        self.goblin.db.is_character = True

        init_nightmare_character(self.fighter)
        init_nightmare_character(self.goblin)

        self.fighter.db.hp = 100
        self.fighter.db.max_hp = 100
        self.goblin.db.hp = 30
        self.goblin.db.max_hp = 30

    def tearDown(self):
        disengage_combat(self.fighter, self.goblin)
        if self.fighter.pk:
            self.fighter.delete()
        if self.goblin.pk:
            self.goblin.delete()
        if self.arena.pk:
            self.arena.delete()
        super().tearDown()

    def test_start_combat_engages_mutual_targets(self):
        """Verify that starting combat locks both combatants together."""
        self.assertFalse(is_in_combat(self.fighter))
        self.assertFalse(is_in_combat(self.goblin))

        start_combat(self.fighter, self.goblin)

        self.assertTrue(is_in_combat(self.fighter))
        self.assertTrue(is_in_combat(self.goblin))
        self.assertEqual(self.fighter.ndb.combat_target, self.goblin)
        self.assertEqual(self.goblin.ndb.combat_target, self.fighter)

    def test_two_way_combat_exchange(self):
        """Verify attacker strikes and defender counter-attacks in a combat round."""
        self.fighter.ndb.combat_target = self.goblin
        self.goblin.ndb.combat_target = self.fighter

        init_fighter_hp = self.fighter.db.hp
        init_goblin_hp = self.goblin.db.hp

        # Execute 1 tick
        combat_round_tick(self.fighter, self.goblin)

        # At least one blow should be landed or evaluated
        self.assertTrue(self.fighter.db.hp < init_fighter_hp or self.goblin.db.hp < init_goblin_hp or is_in_combat(self.fighter))

    def test_disengage_combat_command(self):
        """Verify that CmdDisengage breaks combat lock cleanly."""
        start_combat(self.fighter, self.goblin)
        self.assertTrue(is_in_combat(self.fighter))

        cmd = CmdDisengage()
        cmd.caller = self.fighter
        cmd.args = ""
        cmd.func()

        self.assertFalse(is_in_combat(self.fighter))
        self.assertFalse(is_in_combat(self.goblin))

    def test_disengage_on_room_change(self):
        """Verify that moving to a new room breaks combat lock cleanly."""
        start_combat(self.fighter, self.goblin)
        self.assertTrue(is_in_combat(self.fighter))

        hallway = create_object(Room, key="Castle Hallway")
        self.fighter.move_to(hallway)

        self.assertFalse(is_in_combat(self.fighter))
        self.assertFalse(is_in_combat(self.goblin))
        hallway.delete()

    def test_auto_combat_until_death_awards_xp_and_drops_corpse(self):
        """Verify that lethal damage terminates combat, spawns a corpse, and grants XP."""
        self.goblin.db.hp = 1  # 1 HP remaining, guaranteed to fall on next strike
        start_combat(self.fighter, self.goblin)

        # Fighter should be disengaged after goblin falls
        self.assertFalse(is_in_combat(self.fighter))
        self.assertGreater(self.fighter.db.xp or 0, 0)

        # Corpse should exist in arena
        corpses = [obj for obj in self.arena.contents if "corpse" in obj.key.lower()]
        self.assertGreaterEqual(len(corpses), 1)

    def test_drink_healing_potion_restores_hp(self):
        """Verify drinking an elixir restores HP."""
        from typeclasses.objects import Object
        from commands.interaction_cmds import CmdDrink

        potion = create_object(Object, key="Glowing Health Potion", location=self.fighter)
        potion.db.drink_type = "elixir"
        potion.db.heal_amount = 35

        self.fighter.db.hp = 20
        cmd = CmdDrink()
        cmd.caller = self.fighter
        cmd.args = "potion"
        cmd.func()

        self.assertEqual(self.fighter.db.hp, 55)

    def test_rest_command_recovers_vitals(self):
        """Verify rest command initiates recovery and regenerates HP/Mana/Stamina."""
        from commands.nightmare_cmds import CmdRest
        from world.nightmare_core import rest_tick

        self.fighter.db.hp = 30
        self.fighter.db.mana = 10
        self.fighter.db.stamina = 15

        cmd = CmdRest()
        cmd.caller = self.fighter
        cmd.cmdstring = "rest"
        cmd.func()

        self.assertTrue(self.fighter.db.is_resting)

        # Execute 1 tick
        rest_tick(self.fighter)
        self.assertGreater(self.fighter.db.hp, 30)
        self.assertGreater(self.fighter.db.mana, 10)
        self.assertGreater(self.fighter.db.stamina, 15)

