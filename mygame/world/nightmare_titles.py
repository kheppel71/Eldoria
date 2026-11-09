"""
Nightmare LPmud Player Renown Titles, Heroic Epithets & Accolades Engine.

Implements:
1. Title Prefixes (Sir, Lady, Archmage, Master, Warden).
2. Heroic Epithets (the Dragonslayer, the Goblin's Bane, the Undaunted, the Shadowstalker).
3. Dynamic title unlocking based on quests, levels, and guild milestones.
4. Custom title selection ('titles', 'title set <title>').
"""

DEFAULT_TITLES = {
    "prefixes": ["None", "Sir", "Lady", "Master", "Warden", "Archmage"],
    "epithets": [
        "the Novice Adventurer",
        "the Seasoned Wayfarer",
        "the Goblin's Bane",
        "the Dragonslayer",
        "the Shadowstalker",
        "the Undaunted Champion",
        "the Grand Paragon"
    ]
}


def init_character_titles(char):
    """Initializes title storage on character."""
    if not hasattr(char, "db"):
        return
    if char.db.unlocked_prefixes is None:
        char.db.unlocked_prefixes = ["None"]
    if char.db.unlocked_epithets is None:
        char.db.unlocked_epithets = ["the Novice Adventurer"]
    if char.db.active_prefix is None:
        char.db.active_prefix = "None"
    if char.db.active_epithet is None:
        char.db.active_epithet = "the Novice Adventurer"


def unlock_title(char, title_name, is_prefix=False):
    """Unlocks a new title for the character."""
    init_character_titles(char)
    if is_prefix:
        lst = char.db.unlocked_prefixes or ["None"]
        if title_name not in lst:
            lst.append(title_name)
            char.db.unlocked_prefixes = lst
            char.msg(f"\n|Y[NEW TITLE UNLOCKED]|n You have earned the honorific prefix: |w{title_name}|n!\n")
    else:
        lst = char.db.unlocked_epithets or ["the Novice Adventurer"]
        if title_name not in lst:
            lst.append(title_name)
            char.db.unlocked_epithets = lst
            char.msg(f"\n|Y[NEW EPITHET UNLOCKED]|n You have earned the heroic epithet: |w{title_name}|n!\n")


def set_active_title(char, title_name):
    """Sets active prefix or epithet on character."""
    init_character_titles(char)
    title_clean = title_name.strip()

    prefixes = char.db.unlocked_prefixes or ["None"]
    epithets = char.db.unlocked_epithets or ["the Novice Adventurer"]

    # Match prefix
    matched_prefix = next((p for p in prefixes if title_clean.lower() == p.lower()), None)
    if matched_prefix:
        char.db.active_prefix = matched_prefix
        char.msg(f"|gActive prefix set to: |w{matched_prefix}|n.")
        return True, "Prefix set."

    # Match epithet
    matched_epithet = next((e for e in epithets if title_clean.lower() in e.lower()), None)
    if matched_epithet:
        char.db.active_epithet = matched_epithet
        char.msg(f"|gActive epithet set to: |w{matched_epithet}|n.")
        return True, "Epithet set."

    return False, f"You have not unlocked the title '{title_name}'. Type 'titles' to view your accolades."


def get_full_titled_name(char):
    """Returns the full styled name with active prefix and epithet."""
    init_character_titles(char)
    prefix = char.db.active_prefix
    epithet = char.db.active_epithet

    pref_str = f"{prefix} " if prefix and prefix != "None" else ""
    epi_str = f" {epithet}" if epithet else ""

    return f"{pref_str}{char.key}{epi_str}"

