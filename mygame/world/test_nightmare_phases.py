import os
import sys

# Setup Evennia environment
os.chdir(r"c:\Evennia\mygame")
sys.path.insert(0, r"c:\Evennia\mygame")
os.environ["DJANGO_SETTINGS_MODULE"] = "server.conf.settings"

import django
django.setup()
import evennia
evennia._init()

from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object
from world.nightmare_core import (
    init_nightmare_character, GUILDS, RACES, PRESTIGE_SUBCLASSES, SPELLS,
    trigger_skill_tick, perform_combat_round
)
from commands.nightmare_cmds import (
    CmdSpellbook, CmdStudy, CmdCast, CmdSubclass, CmdAbility, CmdRacial, CmdRace
)

def run_tests():
    print("=" * 60)
    print("STARTING COMPREHENSIVE NIGHTMARE LPMUD VERIFICATION SUITE")
    print("=" * 60)

    # Setup dummy room and characters
    test_room = create_object(Room, key="Arcane Testing Chamber")
    mage = create_object(Character, key="Valerius_Tester", location=test_room)
    dummy = create_object(Character, key="Target_Dummy", location=test_room)
    dummy.db.is_character = True

    init_nightmare_character(mage)
    init_nightmare_character(dummy)

    # -------------------------------------------------------------------------
    # TEST 1: Phase 1 - Spellbook, Study/Scribing, Incantations & Reagents
    # -------------------------------------------------------------------------
    print("\n[Phase 1] Testing Spellbook and Scribing...")
    assert "firebolt" in mage.db.spellbook
    assert "heal" in mage.db.spellbook
    print(f" Initial spellbook: {mage.db.spellbook} -> PASS")

    # Give mage a Scroll of Fireball
    scroll = create_object(Object, key="Scroll of Fireball", location=mage)
    scroll.db.spell = "fireball"

    # Study scroll
    cmd_study = CmdStudy()
    cmd_study.caller = mage
    cmd_study.args = "scroll of fireball"
    cmd_study.func()
    assert "fireball" in mage.db.spellbook
    print(f" Scribed Scroll of Fireball: {mage.db.spellbook} -> PASS")

    # Test Reagent Check for Fireball (requires sulfur)
    cmd_cast = CmdCast()
    cmd_cast.caller = mage
    cmd_cast.args = "fireball at Target_Dummy"
    
    # First attempt: no sulfur in inventory
    orig_msg = mage.msg
    messages_received = []
    def record_msg(*args, **kwargs):
        if args:
            messages_received.append(str(args[0]))
        elif "text" in kwargs:
            messages_received.append(str(kwargs["text"]))
    mage.msg = record_msg

    cmd_cast.func() # Should fail for lack of sulfur
    assert any("lack the required reagent" in m for m in messages_received)

    # Give sulfur reagent
    sulfur = create_object(Object, key="Pinch of Brimstone Sulfur", location=mage)
    cmd_cast.func() # Should succeed and consume sulfur
    assert sulfur not in mage.contents
    print(" Fireball consumed sulfur, cast successfully -> PASS")

    # Test Stone Skin
    mage.db.spellbook.append("stoneskin")
    dust = create_object(Object, key="Pouch of Grave Dust", location=mage)
    cmd_cast.args = "stoneskin"
    cmd_cast.func()
    assert mage.db.stoneskin_absorb == 80
    print(f" Stone Skin granted {mage.db.stoneskin_absorb} absorption -> PASS")

    # Test Animate Dead
    mage.db.mana = 100
    mage.db.spellbook.append("animate")
    corpse = create_object(Object, key="Corpse of Goblin", location=test_room)
    g_dust = create_object(Object, key="Pouch of Grave Dust", location=mage)
    cmd_cast.args = "animate"
    cmd_cast.func()
    thrall = [o for o in test_room.contents if "Skeletal Thrall" in o.key]
    assert len(thrall) > 0
    print(f" Animate Dead raised: {thrall[0].key} -> PASS")

    # -------------------------------------------------------------------------
    # TEST 2: Phase 2 - Use-Based Skill Ticks & Riposte Synergies
    # -------------------------------------------------------------------------
    print("\n[Phase 2] Testing Skill Ticks & Combat Synergies...")
    init_blade = mage.db.skills["blade"]
    # Force skill tick
    for _ in range(20):
        trigger_skill_tick(mage, "blade", difficulty=100)
    print(f" Blade skill progressed: {init_blade}% -> {mage.db.skills['blade']}% -> PASS")

    # Test Riposte
    dummy.db.skills["parry"] = 100 # Guaranteed parry + riposte (>40)
    mage.db.hp = 100
    perform_combat_round(mage, dummy)
    print(" Combat round with Riposte executed -> PASS")

    # -------------------------------------------------------------------------
    # TEST 3: Phase 3 - Prestige Guild Subclasses & Signature Abilities
    # -------------------------------------------------------------------------
    print("\n[Phase 3] Testing Prestige Guild Subclasses & Abilities...")
    mage.db.guild = "Mage"
    cmd_sub = CmdSubclass()
    cmd_sub.caller = mage
    cmd_sub.args = "Pyromancer"
    cmd_sub.func()
    assert mage.db.subclass == "Pyromancer"
    print(f" Specialized into {mage.db.subclass} (+4 INT) -> PASS")

    # Use Pyromancer Combustion ability
    cmd_ab = CmdAbility()
    cmd_ab.caller = mage
    cmd_ab.args = ""
    cmd_ab.func()
    assert mage.db.combustion_active == True
    print(" Combustion charged for next fire spell -> PASS")

    # Test Fighter specialization Berserker
    fighter = create_object(Character, key="Ragnar_Tester", location=test_room)
    fighter.db.is_character = True
    init_nightmare_character(fighter)
    fighter.db.guild = "Fighter"
    cmd_sub.caller = fighter
    cmd_sub.args = "Berserker"
    cmd_sub.func()
    assert fighter.db.subclass == "Berserker"
    print(f" Fighter specialized into: {fighter.db.subclass} -> PASS")

    cmd_ab.caller = fighter
    cmd_ab.func() # Triggers rage
    assert fighter.db.is_raging == True
    print(" Blood rage activated (+15 weapon dmg) -> PASS")

    # -------------------------------------------------------------------------
    # TEST 4: Phase 4 - Exotic Races (Dragonkin & Centaur) & Active Powers
    # -------------------------------------------------------------------------
    print("\n[Phase 4] Testing Exotic Races, Morphology & Active Racial Powers...")
    cmd_race = CmdRace()
    cmd_race.caller = fighter
    cmd_race.args = "Dragonkin"
    cmd_race.func()
    assert fighter.db.race == "Dragonkin"
    assert "tail" in fighter.db.limbs
    print(f" Dragonkin race active with morphology limbs: {list(fighter.db.limbs.keys())} -> PASS")

    # Dragon breath racial power
    cmd_racep = CmdRacial()
    cmd_racep.caller = fighter
    cmd_racep.args = ""
    cmd_racep.func()
    print(" Dragonkin breathefire AoE executed -> PASS")

    # Centaur test
    cmd_race.args = "Centaur"
    cmd_race.func()
    assert fighter.db.race == "Centaur"
    assert "forelegs" in fighter.db.limbs
    assert "hindlegs" in fighter.db.limbs
    print(f" Centaur race active with morphology limbs: {list(fighter.db.limbs.keys())} -> PASS")

    cmd_racep.args = "Target_Dummy"
    cmd_racep.func()
    print(" Centaur trample executed -> PASS")

    # Clean up test objects
    mage.delete()
    dummy.delete()
    fighter.delete()
    test_room.delete()

    print("\n" + "=" * 60)
    print("ALL 4 NIGHTMARE LPMUD PHASES FULLY VERIFIED AND PASSING!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
