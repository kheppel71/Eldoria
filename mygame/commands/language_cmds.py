"""
Nightmare LPmud Language Commands for Evennia
Includes:
- CmdLanguages: View known tongues and fluency %
- CmdSpeak: Set active spoken language
- CmdSayLang: Room-wide speech with dynamic phonetic obfuscation
- CmdWhisperLang: Private targeted whispering with language obfuscation
"""

import random
from evennia import default_cmds
from world.languages import (
    LANGUAGES, obfuscate_sentence, trigger_language_tick, get_innate_languages
)
from world.nightmare_core import init_nightmare_character


def ensure_character_languages(char):
    """Ensures character has active_language and languages dictionary initialized."""
    if not hasattr(char, "db"):
        return
    if not char.db.languages:
        race = getattr(char.db, "race", "Human") or "Human"
        guild = getattr(char.db, "guild", "Fighter") or "Fighter"
        char.db.languages = get_innate_languages(race, guild)
    if not char.db.active_language:
        char.db.active_language = "common"


class CmdLanguages(default_cmds.MuxCommand):
    """
    View your known languages and linguistic fluency

    Usage:
      languages
      langs
    """
    key = "languages"
    aliases = ["langs"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        ensure_character_languages(caller)

        langs = caller.db.languages or {"common": 100}
        active_lang = caller.db.active_language or "common"

        caller.msg("\n|w============================= KNOWN LANGUAGES =============================|n")
        caller.msg(f"{'Language':<14} {'Fluency':<12} {'Status':<12} {'Description':<38}")
        caller.msg("-" * 75)

        for lang_key, data in LANGUAGES.items():
            fluency = langs.get(lang_key, 0)
            if fluency > 0:
                is_active = (lang_key == active_lang)
                status_str = "|g[ACTIVE]|n" if is_active else "|wKnown|n"
                fluency_str = f"|g{fluency}%|n" if fluency >= 100 else f"|y{fluency}%|n"
                caller.msg(f"|c{data['name']:<14}|n {fluency_str:<21} {status_str:<21} {data['desc'][:36]}")

        caller.msg("|w=============================================================================|n")
        caller.msg(f"Current spoken tongue: |g{LANGUAGES.get(active_lang, {}).get('name', 'Common')}|n")
        caller.msg("To change active tongue: |wspeak <language>|n (e.g. speak elven)")
        caller.msg("To speak once in a language: |wsay/<lang> <message>|n\n")


class CmdSpeak(default_cmds.MuxCommand):
    """
    Set your active spoken language

    Usage:
      speak <language>
    """
    key = "speak"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        ensure_character_languages(caller)

        if not self.args:
            caller.msg("Which language do you want to speak? Type |wlanguages|n to see your known tongues.")
            return

        choice = self.args.strip().lower()
        matched_key = None
        for lang_key, data in LANGUAGES.items():
            if choice == lang_key or choice in data["name"].lower():
                matched_key = lang_key
                break

        if not matched_key:
            caller.msg(f"Unknown language '{choice}'. Type |wlanguages|n to check your tongues.")
            return

        langs = caller.db.languages or {}
        fluency = langs.get(matched_key, 0)
        if fluency <= 0:
            caller.msg(f"You do not know how to speak {LANGUAGES[matched_key]['name']}!")
            return

        caller.db.active_language = matched_key
        lang_name = LANGUAGES[matched_key]["name"]
        caller.msg(f"|gYou switch your spoken tongue. You are now speaking in |c{lang_name}|g (Fluency: {fluency}%).|n")


class CmdSayLang(default_cmds.MuxCommand):
    """
    Speak to everyone in the room with dynamic language translation

    Usage:
      say <message>
      say/<language> <message>
      "<message>
      '<message>
    """
    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"
    help_category = "Communication"
    switches = []

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        ensure_character_languages(caller)

        if not self.args:
            caller.msg("Say what?")
            return

        message = self.args.strip()

        # Determine language to use
        lang_key = caller.db.active_language or "common"
        switches = getattr(self, "switches", []) or []
        if switches:
            switch_choice = switches[0].lower()
            for k in LANGUAGES.keys():
                if switch_choice == k or switch_choice in LANGUAGES[k]["name"].lower():
                    lang_key = k
                    break

        langs = caller.db.languages or {}
        fluency = langs.get(lang_key, 0)
        if fluency <= 0:
            lang_name = LANGUAGES.get(lang_key, {}).get("name", lang_key)
            caller.msg(f"You cannot speak in {lang_name} because you do not know the language!")
            return

        lang_name = LANGUAGES.get(lang_key, {}).get("name", "Common")

        # Broadcast to room contents
        location = caller.location
        if not location:
            caller.msg(f'You say, "{message}"')
            return

        for receiver in location.contents:
            if receiver == caller:
                if lang_key == "common":
                    caller.msg(f'|cYou say, |n"{message}"')
                else:
                    caller.msg(f'|cYou say in {lang_name}, |n"{message}"')
            elif hasattr(receiver, "msg"):
                # Determine listener comprehension
                r_fluency = 0
                if hasattr(receiver, "db") and receiver.db.languages:
                    r_fluency = receiver.db.languages.get(lang_key, 0)

                obfuscated = obfuscate_sentence(message, lang_key, r_fluency)

                if lang_key == "common":
                    receiver.msg(f'|c{caller.key} says, |n"{obfuscated}"')
                else:
                    receiver.msg(f'|c{caller.key} says in {lang_name}, |n"{obfuscated}"')

                # Practice tick for listener
                if lang_key != "common" and r_fluency < 100:
                    trigger_language_tick(receiver, lang_key)

        # Practice tick for speaker
        if lang_key != "common" and fluency < 100:
            trigger_language_tick(caller, lang_key)


class CmdWhisperLang(default_cmds.MuxCommand):
    """
    Whisper secretly to a target in a specific language

    Usage:
      whisper <target> = <message>
      whisper/<language> <target> = <message>
    """
    key = "whisper"
    locks = "cmd:all()"
    help_category = "Communication"
    switches = []

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        ensure_character_languages(caller)

        if not getattr(self, "lhs", None) or not getattr(self, "rhs", None):
            caller.msg("Usage: whisper <target> = <message> (or whisper/<lang> <target> = <message>)")
            return

        target = caller.search(self.lhs.strip(), location=caller.location)
        if not target:
            return

        message = self.rhs.strip()

        # Determine language
        lang_key = caller.db.active_language or "common"
        switches = getattr(self, "switches", []) or []
        if switches:
            switch_choice = switches[0].lower()
            for k in LANGUAGES.keys():
                if switch_choice == k or switch_choice in LANGUAGES[k]["name"].lower():
                    lang_key = k
                    break

        langs = caller.db.languages or {}
        fluency = langs.get(lang_key, 0)
        if fluency <= 0:
            lang_name = LANGUAGES.get(lang_key, {}).get("name", lang_key)
            caller.msg(f"You cannot whisper in {lang_name} because you do not know the language!")
            return

        lang_name = LANGUAGES.get(lang_key, {}).get("name", "Common")

        # Speaker feedback
        caller.msg(f'|wYou whisper to {target.key} in {lang_name}: |n"{message}"')

        # Listener feedback
        r_fluency = 0
        if hasattr(target, "db") and target.db.languages:
            r_fluency = target.db.languages.get(lang_key, 0)

        obfuscated = obfuscate_sentence(message, lang_key, r_fluency)
        target.msg(f'|w{caller.key} whispers to you in {lang_name}: |n"{obfuscated}"')

        # Observers notice whispering
        caller.location.msg_contents(
            f"{caller.key} quietly whispers something to {target.key}.",
            exclude=[caller, target]
        )

        if lang_key != "common":
            if r_fluency < 100:
                trigger_language_tick(target, lang_key)
            if fluency < 100:
                trigger_language_tick(caller, lang_key)


class CmdStudyLang(default_cmds.MuxCommand):
    """
    Study language manuscripts at a library or from a language primer

    Usage:
      studylang <language>
      practice <language>
    """
    key = "studylang"
    aliases = ["practice"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        ensure_character_languages(caller)

        if not self.args:
            caller.msg("Which language do you wish to study? (e.g. studylang elven)")
            return

        target_lang = self.args.strip().lower()
        matched_key = None
        for l_key, l_data in LANGUAGES.items():
            if target_lang == l_key or target_lang in l_data["name"].lower():
                matched_key = l_key
                break

        if not matched_key:
            caller.msg(f"Unknown language '{target_lang}'. Check |wlanguages|n for list.")
            return

        if matched_key == "common":
            caller.msg("You are already completely fluent in Common.")
            return

        # Check location or items for learning source
        loc_key = (caller.location.key.lower() if caller.location else "")
        in_library = "library" in loc_key or "scriptorium" in loc_key or "observatory" in loc_key
        has_primer = any("primer" in item.key.lower() or "lexicon" in item.key.lower() or "codex" in item.key.lower() or matched_key in item.key.lower() for item in caller.contents)

        if not in_library and not has_primer:
            caller.msg("You need to be in a study hall (such as the Arcane Library) or carry a language primer/lexicon to study!")
            return

        if (caller.db.stamina or 0) < 15:
            caller.msg("You are too mentally and physically exhausted to study right now! (Requires 15 Stamina)")
            return

        caller.db.stamina -= 15
        langs = caller.db.languages or {}
        curr_val = langs.get(matched_key, 0)
        if curr_val >= 100:
            caller.msg(f"You have already achieved 100% complete mastery of {LANGUAGES[matched_key]['name']}!")
            return

        gain = random.randint(3, 6)
        langs[matched_key] = min(100, curr_val + gain)
        caller.db.languages = langs

        caller.msg(
            f"\n|gYou pour over weathered manuscripts, pronouncing archaic vowels and grammatical declensions...|n\n"
            f"|cYour fluency in {LANGUAGES[matched_key]['name']} increases by +{gain}%! (Now: {langs[matched_key]}%)|n\n"
        )
        caller.location.msg_contents(
            f"{caller.key} studies an arcane linguistic manuscript with intense focus.",
            exclude=[caller]
        )
