"""
Nightmare LPmud Paleontological Fossils, Restoration & Museum Curations Engine.

Implements:
1. Fossil specimens discovered across ancient quarries and caves:
   - Petrified Trilobite Matrix
   - Ancient Mammoth Tusk
   - Fossilized Raptor Talon
   - Gargantuan Wyrm Skull
2. Specimen cleaning and fossil restoration ('cleanspecimen').
3. Praxis Historical Museum donations ('donatemuseum').
4. Museum exhibit gallery and curator prestige ('museum').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

FOSSIL_CATALOG = {
    "trilobite": {
        "raw_name": "Petrified Trilobite Matrix",
        "clean_name": "Pristine Trilobite Fossil",
        "era": "Primordial Age",
        "curator_value": 30,
        "desc": "A segmented arthropod exoskeleton beautifully preserved in dark grey slate."
    },
    "mammoth_tusk": {
        "raw_name": "Weathered Mammoth Tusk",
        "clean_name": "Polished Ancient Mammoth Tusk",
        "era": "Glacial Epoch",
        "curator_value": 55,
        "desc": "A massive spiraling ivory tusk dating back to the primordial ice sheets."
    },
    "raptor_claw": {
        "raw_name": "Crusted Raptor Talon",
        "clean_name": "Serrated Raptor Hunting Talon",
        "era": "Cretaceous Dawn",
        "curator_value": 75,
        "desc": "A lethal curved predatory claw petrified into glossy obsidian-like stone."
    },
    "wyrm_skull": {
        "raw_name": "Earthy Colossal Wyrm Skull",
        "clean_name": "Majestic Draconic Wyrm Skull",
        "era": "Age of Dragons",
        "curator_value": 120,
        "desc": "An imposing horned reptilian skull exhibiting razor-sharp fossilized fangs."
    }
}

MUSEUM_EXHIBITS = []


def create_raw_fossil(location, key="trilobite"):
    """Spawns an uncleaned prehistoric fossil specimen."""
    data = FOSSIL_CATALOG.get(key, FOSSIL_CATALOG["trilobite"])
    fossil = create_object(Object, key=data["raw_name"], location=location)
    fossil.db.is_fossil = True
    fossil.db.fossil_key = key
    fossil.db.is_cleaned = False
    fossil.db.desc = f"An uncleaned fossil specimen encrusted in limestone matrix. Era: {data['era']}."
    return fossil


def clean_fossil_specimen(caller, target_name=""):
    """Cleans away surrounding limestone rock to reveal the preserved fossil."""
    fossil = None
    for obj in caller.contents:
        if getattr(obj.db, "is_fossil", False) and not getattr(obj.db, "is_cleaned", False):
            if not target_name or target_name.lower() in obj.key.lower():
                fossil = obj
                break

    if not fossil:
        return False, "You do not have an uncleaned fossil specimen in your pack to clean."

    key = fossil.db.fossil_key
    data = FOSSIL_CATALOG[key]

    fossil.key = data["clean_name"]
    fossil.db.is_cleaned = True
    fossil.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[FOSSIL RESTORATION]|n With dental picks and fine brass brushes, you chisel away the rocky matrix.\n"
        f"You reveal a magnificent |w{fossil.key}|n ({data['era']})!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} meticulously cleans a prehistoric fossil, uncovering {fossil.key}.",
            exclude=[caller]
        )
    return True, f"Cleaned {fossil.key}."


def donate_fossil_to_museum(caller, target_name=""):
    """Donates a cleaned fossil to the Praxis Museum of Natural History."""
    fossil = None
    for obj in caller.contents:
        if getattr(obj.db, "is_fossil", False) and getattr(obj.db, "is_cleaned", False):
            if not target_name or target_name.lower() in obj.key.lower():
                fossil = obj
                break

    if not fossil:
        return False, "You need a cleaned, restored fossil to donate to the museum archives."

    key = fossil.db.fossil_key
    data = FOSSIL_CATALOG[key]
    reward = data["curator_value"]
    fossil_title = fossil.key

    fossil.delete()

    caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + reward
    caller.db.curator_points = (getattr(caller.db, "curator_points", 0) or 0) + 10

    MUSEUM_EXHIBITS.append({
        "title": fossil_title,
        "era": data["era"],
        "donor": caller.key
    })

    caller.msg(
        f"\n|G[MUSEUM CURATION]|n The Chief Curator gasps in awe at your donation of |w{fossil_title}|n!\n"
        f"Your specimen is mounted in the Great Paleontology Hall.\n"
        f"You receive a preservation grant of |y{reward} gold coins|n and |w+10 Curator Honor|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} donates {fossil_title} to the Museum of Natural History!",
            exclude=[caller]
        )
    return True, "Donated."


def format_museum_display():
    """Formats museum exhibit directory."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w               PRAXIS MUSEUM OF NATURAL HISTORY & PALEONTOLOGY     |n",
        "|c" + "=" * 70 + "|n"
    ]

    if not MUSEUM_EXHIBITS:
        lines.append(" |xThe grand museum display pedestals currently stand empty, awaiting discoveries.|n")
    else:
        for idx, item in enumerate(MUSEUM_EXHIBITS, 1):
            lines.append(f" |Y[{idx}]|n |w{item['title']}|n [Era: |c{item['era']}|n]")
            lines.append(f"     |gDonated by Benefactor:|n {item['donor']}")
            lines.append("     " + "-" * 64)

    lines.append("|c" + "=" * 70 + "|n")
    lines.append("|xCommands: 'cleanspecimen <fossil>', 'donatemuseum <fossil>', 'museum'|n")
    return "\n".join(lines)

