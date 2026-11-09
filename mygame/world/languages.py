"""
Nightmare LPmud Linguistic System for Evennia
Features:
1. Dynamic Phonetic Obfuscation per Language
2. Fluency Progression & Comprehension Ticks
3. Innate Racial & Guild Tongue Proficiencies
4. Room-Wide Multilingual Say and Targeted Whisper
"""

import random
import re

# =============================================================================
# LANGUAGE DEFINITIONS & PHONETIC DICTIONARIES
# =============================================================================

LANGUAGES = {
    "common": {
        "name": "Common",
        "desc": "The universal trade tongue spoken across all kingdoms and provinces.",
        "phonemes": None
    },
    "elven": {
        "name": "Elven",
        "desc": "A flowing, melodic cadence of the ancient woodland elves.",
        "prefix": ["sha", "vae", "ely", "ala", "syl", "thas", "fen", "lor", "cael", "ari"],
        "mid": ["'lan", "'dor", "'tis", "'ren", "'val", "'mir", "'en", "'lith"],
        "suffix": ["ath", "iel", "or", "eth", "is", "a", "ae", "wyn", "ore"]
    },
    "dwarven": {
        "name": "Dwarven",
        "desc": "A hard, guttural tongue carved like granite, iron, and mountain stone.",
        "prefix": ["khaz", "drak", "bar", "thung", "gor", "mor", "krag", "grum", "vond"],
        "mid": ["'ak", "'bur", "'gar", "'rik", "'dum", "'nor", "'thul"],
        "suffix": ["im", "uk", "or", "in", "az", "und", "rak", "ad"]
    },
    "drow": {
        "name": "Drow",
        "desc": "Sibilant, whispered dialects spoken in subterranean shadow caverns.",
        "prefix": ["z'res", "szy", "xun", "drak", "ssin", "qu'el", "vel", "phalar", "inith"],
        "mid": ["'ath", "'il", "'dra", "'zar", "'vlos", "'xik"],
        "suffix": ["ryn", "iss", "ael", "zair", "oth", "rae", "nin"]
    },
    "draconic": {
        "name": "Draconic",
        "desc": "An ancient, roaring reptilian language of flame, wyrms, and raw magic.",
        "prefix": ["dra'kosh", "vor'na", "py'rak", "vax", "ignar", "char'goth", "saur", "khor"],
        "mid": ["'kar", "'morth", "'vash", "'drak", "'gor", "'zod"],
        "suffix": ["ox", "ath", "ys", "ar", "um", "ex", "ul", "thos"]
    },
    "centaur": {
        "name": "Centaur",
        "desc": "A rhythmic, galloping nomadic tongue echoing across untamed steppes.",
        "prefix": ["hrav", "trot", "khan", "step", "stram", "thun", "vrak", "roam"],
        "mid": ["'kor", "'dan", "'gath", "'ram", "'vek", "'hoof"],
        "suffix": ["ar", "en", "ok", "ash", "ur", "an", "on"]
    },
    "halfling": {
        "name": "Halfling",
        "desc": "A rapid, cheerful dialect peppered with homey idioms and chirps.",
        "prefix": ["pip", "nib", "bop", "flit", "churp", "wisp", "top", "perk"],
        "mid": ["'kin", "'lin", "'ton", "'by", "'wee", "'hop"],
        "suffix": ["le", "kin", "ock", "et", "y", "ling", "ump"]
    },
    "celestial": {
        "name": "Celestial",
        "desc": "Harmonic, resonant choral language spoken in astral cathedrals.",
        "prefix": ["ae'ter", "lux", "sanc", "glor", "cael", "di'vin", "sol", "cura"],
        "mid": ["'tis", "'or", "'an", "'um", "'el", "'ser"],
        "suffix": ["us", "a", "is", "orum", "el", "ia", "as"]
    },
    "goblinoid": {
        "name": "Goblinoid",
        "desc": "Harsh, snarling gutter-speak of raiders, skulkers, and scavengers.",
        "prefix": ["skrik", "blud", "guk", "snag", "krump", "snark", "zag", "skab"],
        "mid": ["'nak", "'gash", "'grot", "'bog", "'snick", "'rip"],
        "suffix": ["it", "argh", "ok", "uk", "ug", "ak", "gob"]
    }
}


# =============================================================================
# PHONETIC OBFUSCATION ENGINE
# =============================================================================

def scramble_word(word, lang_key):
    """
    Transforms an English word into a pseudo-language phoneme matching
    the phonetic dictionary of lang_key.
    Uses hash(word) for determinism so identical words scramble identically.
    """
    if not word or lang_key == "common":
        return word

    lang_data = LANGUAGES.get(lang_key)
    if not lang_data or not lang_data.get("prefix"):
        return word

    # Strip punctuation to preserve it outside the scrambled word
    prefix_punct = ""
    suffix_punct = ""
    core_word = word

    while core_word and not core_word[0].isalnum():
        prefix_punct += core_word[0]
        core_word = core_word[1:]
    while core_word and not core_word[-1].isalnum():
        suffix_punct = core_word[-1] + suffix_punct
        core_word = core_word[:-1]

    if not core_word:
        return word

    # Deterministic seed based on lowercase word
    w_hash = abs(hash(core_word.lower()))
    prefixes = lang_data["prefix"]
    mids = lang_data.get("mid", [""])
    suffixes = lang_data["suffix"]

    pref = prefixes[w_hash % len(prefixes)]
    suff = suffixes[(w_hash // 7) % len(suffixes)]

    if len(core_word) > 5:
        mid = mids[(w_hash // 13) % len(mids)]
        garbled = f"{pref}{mid}{suff}"
    else:
        garbled = f"{pref}{suff}"

    # Match capitalization
    if core_word.isupper():
        garbled = garbled.upper()
    elif core_word[0].isupper():
        garbled = garbled.capitalize()

    return prefix_punct + garbled + suffix_punct


def obfuscate_sentence(text, lang_key, listener_fluency=0):
    """
    Obfuscates an entire sentence for a listener based on listener_fluency (0-100%).
    At 100% fluency, the text is completely clear.
    At 0% fluency, every word is garbled into phonemes.
    At intermediate fluency, some words are understood and others are garbled.
    """
    if lang_key == "common" or listener_fluency >= 100:
        return text

    words = text.split()
    scrambled = []

    for word in words:
        # Check if listener understands this particular word based on fluency
        # Deterministic roll per word hash mixed with fluency
        word_roll = (abs(hash(word.lower())) % 100) + 1
        if word_roll <= listener_fluency:
            scrambled.append(word)
        else:
            scrambled.append(scramble_word(word, lang_key))

    return " ".join(scrambled)


# =============================================================================
# PROFICIENCY ADVANCEMENT TICKS
# =============================================================================

def trigger_language_tick(char, lang_key):
    """
    Organic language skill tick when speaking or hearing a foreign tongue.
    Chance to increase fluency by 1% based on character Intelligence.
    """
    if not hasattr(char, "db") or not char.db.languages:
        return

    if lang_key == "common":
        return

    langs = char.db.languages
    curr_val = langs.get(lang_key, 0)
    if curr_val >= 100:
        return

    intel = getattr(char.db, "int", 12)
    chance = max(5, int((100 - curr_val) * 0.25) + (intel // 3))

    if random.randint(1, 100) <= chance:
        langs[lang_key] = curr_val + 1
        lang_name = LANGUAGES[lang_key]["name"]
        char.msg(f"|gYour comprehension of {lang_name} improves! ({curr_val}% -> {curr_val + 1}%)|n")


# =============================================================================
# INNATE PROFICIENCIES BY RACE & GUILD
# =============================================================================

def get_innate_languages(race="Human", guild="Fighter"):
    """Returns starting language dictionary for a given race and guild."""
    langs = {"common": 100}

    # Racial mother tongues
    if race == "Elf":
        langs["elven"] = 100
        langs["celestial"] = 40
    elif race == "Dwarf":
        langs["dwarven"] = 100
        langs["goblinoid"] = 25
    elif race == "Drow":
        langs["drow"] = 100
        langs["elven"] = 50
    elif race == "Dragonkin":
        langs["draconic"] = 100
    elif race == "Centaur":
        langs["centaur"] = 100
        langs["elven"] = 30
    elif race == "Halfling":
        langs["halfling"] = 100
    elif race == "Human":
        # Humans are adaptable, get a random worldly language at 35%
        bonus_lang = random.choice(["elven", "dwarven", "halfling", "centaur"])
        langs[bonus_lang] = 35

    # Guild cultural tongues
    if guild in ["Cleric", "Healer", "Inquisitor"]:
        langs["celestial"] = max(langs.get("celestial", 0), 75)
    elif guild in ["Mage", "Pyromancer", "Conjurer"]:
        langs["draconic"] = max(langs.get("draconic", 0), 40)
        langs["celestial"] = max(langs.get("celestial", 0), 40)
    elif guild in ["Rogue", "Assassin", "Shadowthief"]:
        langs["drow"] = max(langs.get("drow", 0), 40)
        langs["goblinoid"] = max(langs.get("goblinoid", 0), 50)
    elif guild in ["Ranger", "Beastmaster", "Sniper"]:
        langs["elven"] = max(langs.get("elven", 0), 50)
        langs["centaur"] = max(langs.get("centaur", 0), 40)

    return langs

