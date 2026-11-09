"""
Nightmare LPmud Grand Library Archives, Lore Tomes & Archaeological Research Engine.

Implements:
1. Ancient Lore Tomes & Codices:
   - Chronicles of the Goblin Wars
   - Codex of Abyssal Necromancy
   - Tome of Ancient Architecture & Traps
   - Lexicon of the Old Gods
2. Scholarly Study ('readtome', 'studytome') granting permanent Lore Points
   and historical enlightenment.
3. Transcription of parchment scrolls ('transcribe').
4. Comprehensive Scholar Lore Dossier ('lore', 'scholar').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

LORE_TOMES = {
    "goblin_wars": {
        "title": "Chronicles of the Goblin Wars",
        "author": "Archivist Valerius the Elder",
        "lore_points": 15,
        "desc": "A thick, leather-bound volume recounting the bloody sieges of the Goblin Khans against Praxis.",
        "excerpt": (
            "In the Third Age of Reckoning, the Goblin Khans amassed twenty thousand warriors at the Eastern Gate. "
            "Their warlords forged weapons of jagged black iron tempered in blood. Only by collapsing the subterranean "
            "tunnels did the High Council break the siege, driving the remnants into the dark crags..."
        )
    },
    "abyssal_codex": {
        "title": "Codex of Abyssal Necromancy",
        "author": "Morgrath the Exiled",
        "lore_points": 25,
        "desc": "A sinister codex bound in cold leathery hide, locked with a silver clasp.",
        "excerpt": (
            "The nether rifts open when mortal agony aligns with astral conjunctions. "
            "Blood sacrificed under the Blood Moon pierces the veil between realms, awakening resting spectres "
            "and granting eternal life to those willing to surrender their pulse..."
        )
    },
    "ancient_architecture": {
        "title": "Tome of Ancient Architecture & Traps",
        "author": "Master Mason Haldor",
        "lore_points": 20,
        "desc": "A vellum notebook brimming with architectural sketches, floor traps, and concealed brick mechanisms.",
        "excerpt": (
            "Dwarven subterranean vaults invariably favor pressure-sensitive flagstones set three paces before heavy entry archways. "
            "Look always to the ceiling for counterweight grooves and release apertures before proceeding..."
        )
    },
    "old_gods": {
        "title": "Lexicon of the Old Gods",
        "author": "High Priestess Selene",
        "lore_points": 20,
        "desc": "An illuminated gilded manuscript adorned with star charts and divine mantras.",
        "excerpt": (
            "Before the stone cities were raised, the primordial deities walked upon the earth in forms of storm and starlight. "
            "Those who honor the sacred shrines with offerings of gold and incense shall never walk in darkness..."
        )
    }
}


def create_lore_tome(location, tome_key="goblin_wars"):
    """Spawns an ancient lore tome."""
    data = LORE_TOMES.get(tome_key, LORE_TOMES["goblin_wars"])
    tome = create_object(Object, key=data["title"], location=location)
    tome.db.is_lore_tome = True
    tome.db.tome_key = tome_key
    tome.db.author = data["author"]
    tome.db.lore_points = data["lore_points"]
    tome.db.excerpt = data["excerpt"]
    tome.db.desc = data["desc"]
    return tome


def read_lore_tome(caller, tome_obj):
    """Studies and deciphers a lore tome."""
    if not getattr(tome_obj.db, "is_lore_tome", False):
        return False, f"{tome_obj.key} is not an ancient scholarly tome."

    tome_key = tome_obj.db.tome_key
    read_list = getattr(caller.db, "studied_tomes", []) or []

    # Check if first time reading
    is_new = tome_key not in read_list
    if is_new:
        read_list.append(tome_key)
        caller.db.studied_tomes = read_list
        lp = getattr(tome_obj.db, "lore_points", 15)
        caller.db.lore_points = (getattr(caller.db, "lore_points", 0) or 0) + lp
        bonus_msg = f"\n|Y[LORE DISCOVERY]|n You absorb the historical knowledge, gaining |w+{lp} Lore Points|n!\n"
    else:
        bonus_msg = "\n|x(You have previously studied this volume, refreshing your memory.)|n\n"

    caller.msg(
        f"\n|c" + "=" * 70 + "|n\n"
        f"|w{tome_obj.key}|n by |y{tome_obj.db.author}|n\n"
        f"|c" + "-" * 70 + "|n\n"
        f"|w\"{tome_obj.db.excerpt}\"|n\n"
        f"|c" + "=" * 70 + "|n"
        f"{bonus_msg}"
    )

    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} deeply examines the yellowed parchment pages of {tome_obj.key}.",
            exclude=[caller]
        )
    return True, "Tome studied."


def transcribe_lore_tome(caller, tome_obj):
    """Transcribes a lore tome into a scholarly parchment note."""
    if not getattr(tome_obj.db, "is_lore_tome", False):
        return False, f"{tome_obj.key} is not a valid lore tome to transcribe."

    scroll = create_object(Object, key=f"Scholarly Notes on {tome_obj.key}", location=caller)
    scroll.db.desc = f"Handwritten parchment transcription of {tome_obj.key}, penned by {caller.key}."
    scroll.db.is_parchment = True

    caller.msg(
        f"\n|YYou dip a quill in ink and meticulously transcribe key passages from {tome_obj.key} into |w{scroll.key}|Y!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} carefully pens scholarly transcriptions from {tome_obj.key}.",
            exclude=[caller]
        )
    return True, "Transcribed."


def format_lore_profile(caller):
    """Renders the player's archaeological and scholar lore profile."""
    total_lp = getattr(caller.db, "lore_points", 0) or 0
    read_list = getattr(caller.db, "studied_tomes", []) or []

    # Determine scholar title
    if total_lp >= 100:
        scholar_rank = "Grand Loremaster of the High Archives"
    elif total_lp >= 50:
        scholar_rank = "Senior Chronicler"
    elif total_lp >= 20:
        scholar_rank = "Inquisitive Scholar"
    else:
        scholar_rank = "Novice Apprentice"

    lines = [
        "|c" + "=" * 70 + "|n",
        "|w                   ARCHAEOLOGICAL LORE & SCHOLAR DOSSIER          |n",
        "|c" + "=" * 70 + "|n",
        f" |wScholar Name:|n |c{caller.key}|n",
        f" |yAcademic Standing:|n |w{scholar_rank}|n",
        f" |gCumulative Lore Knowledge:|n |G{total_lp} Lore Points|n",
        f" |mAncient Volumes Mastered:|n {len(read_list)} tomes",
        "|c" + "-" * 70 + "|n",
        " |wStudied Manuscripts Annals:|n"
    ]

    if not read_list:
        lines.append("   |xNo ancient tomes have been recorded in your scholarly journal yet.|n")
    else:
        for tkey in read_list:
            tinfo = LORE_TOMES.get(tkey, {"title": tkey.replace("_", " ").title(), "author": "Unknown"})
            lines.append(f"   |G[*]|n |w{tinfo['title']}|n (|y{tinfo['author']}|n)")

    lines.append("|c" + "=" * 70 + "|n")
    lines.append("|xTo study manuscripts: 'readtome <tome>', or copy with 'transcribe <tome>'.|n")
    return "\n".join(lines)

