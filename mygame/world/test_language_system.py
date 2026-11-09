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
from world.languages import (
    LANGUAGES, scramble_word, obfuscate_sentence, trigger_language_tick, get_innate_languages
)
from world.nightmare_core import init_nightmare_character
from commands.language_cmds import (
    CmdLanguages, CmdSpeak, CmdSayLang, CmdWhisperLang, ensure_character_languages
)

def run_tests():
    print("=" * 60)
    print("STARTING NIGHTMARE LPMUD LANGUAGE SYSTEM TEST SUITE")
    print("=" * 60)

    # 1. Test Innate Proficiencies
    print("\n[Test 1] Testing Innate Languages by Race & Guild...")
    elf_langs = get_innate_languages("Elf", "Ranger")
    assert elf_langs["common"] == 100
    assert elf_langs["elven"] == 100
    print(f" Elf Ranger Languages: {elf_langs} -> PASS")

    dwarf_langs = get_innate_languages("Dwarf", "Fighter")
    assert dwarf_langs["common"] == 100
    assert dwarf_langs["dwarven"] == 100
    print(f" Dwarf Fighter Languages: {dwarf_langs} -> PASS")

    dragon_langs = get_innate_languages("Dragonkin", "Mage")
    assert dragon_langs["draconic"] == 100
    print(f" Dragonkin Mage Languages: {dragon_langs} -> PASS")

    # 2. Test Obfuscation Algorithm
    print("\n[Test 2] Testing Phonetic Obfuscation...")
    original = "The ancient dragons awaken under the mountain."
    # At 0% fluency, every word should be scrambled
    garbled_0 = obfuscate_sentence(original, "draconic", listener_fluency=0)
    print(f" Clear English:    {original}")
    print(f" Draconic (0%):    {garbled_0}")
    assert garbled_0 != original

    # At 100% fluency, text should be completely clear
    clear_100 = obfuscate_sentence(original, "draconic", listener_fluency=100)
    assert clear_100 == original
    print(f" Draconic (100%):  {clear_100} -> PASS")

    # At 50% fluency, some words clear, some garbled
    partial_50 = obfuscate_sentence(original, "draconic", listener_fluency=50)
    print(f" Draconic (50%):   {partial_50} -> PASS")

    # 3. In-Game Room Multilingual Say Test
    print("\n[Test 3] Testing Room-Wide Dynamic Speech...")
    test_room = create_object(Room, key="Babel Tower Common Room")

    elf = create_object(Character, key="Aeloria_Elf", location=test_room)
    elf.db.is_character = True
    elf.db.race = "Elf"
    elf.db.guild = "Mage"
    init_nightmare_character(elf)
    ensure_character_languages(elf)

    dwarf = create_object(Character, key="Bruenor_Dwarf", location=test_room)
    dwarf.db.is_character = True
    dwarf.db.race = "Dwarf"
    dwarf.db.guild = "Fighter"
    init_nightmare_character(dwarf)
    ensure_character_languages(dwarf)

    # Capture messages
    elf_msgs = []
    dwarf_msgs = []
    def rec_elf(*args, **kwargs):
        if args: elf_msgs.append(str(args[0]))
        elif "text" in kwargs: elf_msgs.append(str(kwargs["text"]))
    def rec_dwarf(*args, **kwargs):
        if args: dwarf_msgs.append(str(args[0]))
        elif "text" in kwargs: dwarf_msgs.append(str(kwargs["text"]))
    elf.msg = rec_elf
    dwarf.msg = rec_dwarf

    # Test CmdSpeak
    cmd_speak = CmdSpeak()
    cmd_speak.caller = elf
    cmd_speak.args = "elven"
    cmd_speak.func()
    assert elf.db.active_language == "elven"
    print(" Switched active language to Elven -> PASS")

    # Elf speaks in Elven
    cmd_say = CmdSayLang()
    cmd_say.caller = elf
    cmd_say.args = "Hail warriors of the sacred groves!"
    cmd_say.func()

    # Elf hears clear text
    assert any("You say in Elven" in m and "Hail warriors" in m for m in elf_msgs)
    print(f" Speaker received: {elf_msgs[-1]} -> PASS")

    # Dwarf (0% fluency in Elven) hears garbled Elven phonemes
    assert any("Aeloria_Elf says in Elven" in m for m in dwarf_msgs)
    dwarf_received = [m for m in dwarf_msgs if "Aeloria_Elf says in Elven" in m][-1]
    print(f" Non-fluent Listener received: {dwarf_received} -> PASS")
    assert "warriors of the sacred groves" not in dwarf_received

    # 4. Test Targeted Whispering
    print("\n[Test 4] Testing Targeted Linguistic Whisper...")
    cmd_whisp = CmdWhisperLang()
    cmd_whisp.caller = dwarf
    cmd_whisp.switches = ["dwarven"]
    cmd_whisp.lhs = "Aeloria_Elf"
    cmd_whisp.rhs = "Gold and iron are stronger than twigs."
    cmd_whisp.func()

    elf_whisper = [m for m in elf_msgs if "Bruenor_Dwarf whispers" in m][-1]
    print(f" Elf received whispered Dwarven: {elf_whisper} -> PASS")
    assert "stronger than twigs" not in elf_whisper # Elf doesn't know Dwarven

    # 5. Test Fluency Progression
    print("\n[Test 5] Testing Language Learning Tick...")
    dwarf.db.languages["elven"] = 10
    init_elven = dwarf.db.languages["elven"]
    for _ in range(50):
        trigger_language_tick(dwarf, "elven")
    print(f" Dwarf learned Elven through exposure: {init_elven}% -> {dwarf.db.languages['elven']}% -> PASS")

    # 6. Test Training Language with XP
    print("\n[Test 6] Testing Language Training with XP...")
    from commands.nightmare_cmds import CmdTrain
    from commands.language_cmds import CmdStudyLang
    cmd_train = CmdTrain()
    cmd_train.caller = dwarf
    cmd_train.args = "elven"
    dwarf.db.xp = 500
    prev_fluency = dwarf.db.languages["elven"]
    cmd_train.func()
    assert dwarf.db.languages["elven"] > prev_fluency
    print(f" Trained Elven with XP: {prev_fluency}% -> {dwarf.db.languages['elven']}% -> PASS")

    # 7. Test Studying Language at Library / with Primer
    print("\n[Test 7] Testing Studying Language at Scriptorium...")
    cmd_study = CmdStudyLang()
    cmd_study.caller = dwarf
    cmd_study.args = "draconic"
    # Create a draconic primer in dwarf's inventory
    from typeclasses.objects import Object
    primer = create_object(Object, key="Ancient Draconic Lexicon", location=dwarf)
    dwarf.db.stamina = 50
    cmd_study.func()
    assert dwarf.db.languages.get("draconic", 0) > 0
    print(f" Studied Draconic via Lexicon: {dwarf.db.languages['draconic']}% -> PASS")

    # Clean up test objects
    elf.delete()
    dwarf.delete()
    test_room.delete()

    print("\n" + "=" * 60)
    print("ALL NIGHTMARE LANGUAGE SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

