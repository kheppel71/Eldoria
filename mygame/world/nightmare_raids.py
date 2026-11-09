"""
Nightmare LPmud Dynamic World Boss Raids & Town Invasions Engine.

Implements:
1. Dynamic Town Invasions and Realm-wide World Boss Raids.
2. Incursion encounters with Bosses and minions (Goblin Warlords, Abyssal Incursions, Undead Scourge).
3. Realm Herald alerts and zone invasion statuses.
4. Town Defense Medals and raid participant accolades.
5. Incursion inspection command ('events' / 'raids').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

RAID_DEFINITIONS = {
    "goblin_siege": {
        "title": "Goblin Warlord Siege",
        "location_name": "Town Gates",
        "boss_name": "Gorguk Skullcleaver",
        "boss_hp": 850,
        "boss_level": 10,
        "desc": "A hulking, armor-clad goblin warlord wielding a jagged blood-stained greataxe!",
        "threat": "High",
        "reward_item": "Praxis Defender's Medal",
        "reward_desc": "A gleaming bronze cross engraved with the city crest, awarded for valor in town defense."
    },
    "abyssal_rift": {
        "title": "Abyssal Dread Incursion",
        "location_name": "Temple Crossroads",
        "boss_name": "Xul'Kareth the Soulflayer",
        "boss_hp": 1500,
        "boss_level": 20,
        "desc": "A towering abyssal fiend surrounded by swirling void embers and screams of the damned!",
        "threat": "Extreme",
        "reward_item": "Praxis Defender's Medal",
        "reward_desc": "A gleaming bronze cross engraved with the city crest, awarded for valor in town defense."
    },
    "undead_scourge": {
        "title": "Undead Catacomb Uprising",
        "location_name": "Cemetery Crypts",
        "boss_name": "Lord Malakor the Death Knight",
        "boss_hp": 1100,
        "boss_level": 15,
        "desc": "An ancient spectral knight encased in frosted black plate, wielding a frostbound runeblade!",
        "threat": "Very High",
        "reward_item": "Praxis Defender's Medal",
        "reward_desc": "A gleaming bronze cross engraved with the city crest, awarded for valor in town defense."
    }
}

ACTIVE_RAIDS = {}


def start_raid(raid_id, room=None):
    """Spawns an active town invasion or world boss raid."""
    if raid_id not in RAID_DEFINITIONS:
        return False, f"Unknown raid event '{raid_id}'."

    template = RAID_DEFINITIONS[raid_id]
    boss_obj = None

    if room:
        boss_obj = create_object(Object, key=template["boss_name"], location=room)
        boss_obj.db.is_raid_boss = True
        boss_obj.db.raid_id = raid_id
        boss_obj.db.hp = template["boss_hp"]
        boss_obj.db.max_hp = template["boss_hp"]
        boss_obj.db.level = template["boss_level"]
        boss_obj.db.desc = template["desc"]

        room.msg_contents(
            f"\n|R[REALM INVASION]|n |wThe earth trembles as |r{template['boss_name']}|w breaches the perimeter at {template['location_name']}!|n\n"
        )

    ACTIVE_RAIDS[raid_id] = {
        "template": template,
        "boss_obj": boss_obj,
        "status": "Active",
        "location": room.key if room else template["location_name"]
    }
    return True, f"Invasion '{template['title']}' launched successfully."


def end_raid(raid_id, killer=None):
    """Ends a raid event and awards the slayer."""
    if raid_id not in ACTIVE_RAIDS:
        return False, f"No active raid event with id '{raid_id}'."

    raid = ACTIVE_RAIDS.pop(raid_id)
    template = raid["template"]
    boss_obj = raid.get("boss_obj")

    if boss_obj and boss_obj.pk:
        boss_obj.delete()

    if killer:
        # Award defender medal
        medal = create_object(Object, key=template["reward_item"], location=killer)
        medal.db.desc = template["reward_desc"]
        medal.db.is_medal = True
        killer.msg(
            f"\n|Y[VICTORY]|n You delivered the final blow to |r{template['boss_name']}|n!\n"
            f"You are awarded the |w{template['reward_item']}|n!\n"
        )

    return True, f"Raid '{template['title']}' concluded."


def get_active_raids():
    """Returns currently active raids."""
    return ACTIVE_RAIDS


def format_raids_display():
    """Formats active events and invasions for player viewing."""
    lines = [
        "|c" + "=" * 68 + "|n",
        "|w                   REALM INVASIONS & WORLD BOSS RAIDS            |n",
        "|c" + "=" * 68 + "|n"
    ]

    if not ACTIVE_RAIDS:
        lines.append(" |gNo hostile incursions currently threaten the realm. All gates secure.|n")
    else:
        for rid, data in ACTIVE_RAIDS.items():
            tmpl = data["template"]
            lines.append(f" |R[INVASION]|n |w{tmpl['title']}|n")
            lines.append(f"   |yTarget Location:|n {data['location']}")
            lines.append(f"   |rBoss Entity:|n {tmpl['boss_name']} (Lvl {tmpl['boss_level']})")
            lines.append(f"   |mThreat Level:|n {tmpl['threat']} | |gReward:|n {tmpl['reward_item']}")
            lines.append("   " + "-" * 64)

    lines.append("|c" + "=" * 68 + "|n")
    lines.append("|xType 'events' or 'raids' at any time to monitor realm siege conditions.|n")
    return "\n".join(lines)

