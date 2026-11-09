"""
Nightmare LPmud Guild War Banners, Standards & Warhorns Engine.

Implements:
1. Gilded Guild War Banners and Heraldic Standards.
2. Planting battlefield standards ('plantbanner') granting Courage Auras (+Defense/Morale).
3. Uprooting banners on the march ('uprootbanner').
4. Resonant Rallying Warhorns ('blowwarhorn').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_guild_war_banner(location, guild_name="The Praxian Guard"):
    """Spawns an embroidered guild battle standard."""
    banner = create_object(Object, key=f"{guild_name} Battle Standard", location=location)
    banner.db.is_war_banner = True
    banner.db.guild_name = guild_name
    banner.db.is_planted = False
    banner.db.desc = f"A towering silk and gold-fringed war standard emblazoned with the roaring crest of {guild_name}."
    return banner


def plant_war_banner(caller):
    """Plants a war banner into the ground, inspiring all allies present."""
    banner = None
    for obj in caller.contents:
        if getattr(obj.db, "is_war_banner", False):
            banner = obj
            break

    if not banner:
        return False, "You do not have a Guild Battle Standard in your pack to plant! ('plantbanner')"

    room = caller.location
    if not room:
        return False, "You cannot plant a banner in the void."

    banner.move_to(room, quiet=True)
    banner.db.is_planted = True
    banner.db.planted_by = caller

    caller.msg(
        f"\n|Y[BATTLE STANDARD PLANTED]|n You slam the iron-shod spear butt of {banner.key} deep into the earth!\n"
        "The glorious heraldic silk catches the wind and billows defiantly!\n"
        "|gAura of Courage emanates: All allies in the room gain +15% Armor Fortitude and Morale!|n\n"
    )
    if room:
        room.msg_contents(
            f"|Y*THUMP!* {caller.key} plants the towering {banner.key} firmly into the ground, rallying all allies!|n",
            exclude=[caller]
        )
    return True, "Banner planted."


def uproot_war_banner(caller):
    """Uproots a planted war banner to take on the march."""
    room = caller.location
    banner = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_war_banner", False) and getattr(obj.db, "is_planted", False):
            banner = obj
            break

    if not banner:
        return False, "There is no planted battle standard here to uproot."

    banner.move_to(caller, quiet=True)
    banner.db.is_planted = False

    caller.msg(f"\n|yYou pull the iron butt of {banner.key} from the ground and rest the pole on your shoulder.|n\n")
    if room:
        room.msg_contents(f"{caller.key} uproots {banner.key} and prepares to march.", exclude=[caller])
    return True, "Banner uprooted."


def sound_rallying_warhorn(caller):
    """Blows a deep martial horn to rally companions."""
    caller.msg(
        "\n|R*BWAAARRRRRRRROOOOO!*|n You raise the curved warhorn and blow a thunderous martial blast!\n"
        "The deafening call reverberates across the hills, stiffening the spines of your comrades!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"|R*BWAAARRRRROOOOO!* {caller.key} sounds a booming warhorn that echoes across the battlefield!|n",
            exclude=[caller]
        )
    return True, "Warhorn sounded."

