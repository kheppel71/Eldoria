"""
Nightmare LPmud Finger, Plan & Immortal Suite.

Implements:
1. 'finger <player>': In-depth player dossier with race, guild, quest rank,
   online status, idle time, and personal .plan bio.
2. 'plan <text>': Edits the player's personal .plan profile.
3. Immortal Tools: 'invis'/'vis' ethereal invisibility, 'goto', 'trans', 'destruct'.
"""

import time
from evennia.objects.models import ObjectDB
from world.nightmare_quests import get_quest_rank


def get_finger_data(target):
    """Compiles a complete Nightmare player dossier for target."""
    if not target or not hasattr(target, "db"):
        return None

    race = getattr(target.db, "race", "Human") or "Human"
    guild = getattr(target.db, "guild", "Adventurer") or "Adventurer"
    subclass = getattr(target.db, "subclass", None)
    class_str = f"{guild}/{subclass}" if subclass else guild
    level = getattr(target.db, "level", 1) or 1
    qp = getattr(target.db, "qp", 0) or 0
    q_rank = get_quest_rank(qp)

    # Online / Session check
    sessions = target.sessions.all()
    if sessions:
        idle_secs = int(sessions[0].cmd_last_visible) if hasattr(sessions[0], "cmd_last_visible") else 0
        idle_mins = (int(time.time()) - idle_secs) // 60 if idle_secs else 0
        status_str = f"|gOnline|n (Idle: {idle_mins}m)"
    else:
        status_str = "|xOffline|n"

    plan = getattr(target.db, "plan", "No plan on file.") or "No plan on file."
    bounty = getattr(target.db, "bounty", 0) or 0
    outlaw_str = f" |r[OUTLAW - {bounty}g Bounty]|n" if getattr(target.db, "is_outlaw", False) else ""

    dossier = f"""
|b==============================================================================|n
|w                             N I G H T M A R E                                |n
|b==============================================================================|n
Name: |c{target.key}|n{outlaw_str}
Race: |y{race:<18}|n Guild / Class: |m{class_str}|n
Level: |w{level:<17}|n Quest Standing: {q_rank} ({qp} QP)
Status: {status_str}

|wPlan:|n
  {plan}
|b==============================================================================|n
"""
    return dossier.strip()


def set_player_plan(char, plan_text):
    """Updates the player's personal .plan bio."""
    char.db.plan = plan_text.strip()
    char.msg(f"|gYour .plan bio has been updated! (View with: |wfinger {char.key}|g)|n")
    return True


def toggle_invis(wizard):
    """Toggles wizard ethereal invisibility."""
    is_inv = getattr(wizard.db, "is_invis", False)
    wizard.db.is_invis = not is_inv

    if wizard.db.is_invis:
        wizard.msg("|M*** ETHEREAL INVISIBILITY ACTIVE *** You vanish from mortal sight.|n")
        if wizard.location:
            wizard.location.msg_contents(
                f"|mWith a soft distortion of the air, {wizard.key} fades from view.|n",
                exclude=[wizard]
            )
    else:
        wizard.msg("|M*** ETHEREAL INVISIBILITY DISABLED *** You manifest back into physical sight.|n")
        if wizard.location:
            wizard.location.msg_contents(
                f"|mLight bends and coalesces as {wizard.key} appears out of thin air.|n",
                exclude=[wizard]
            )
    return wizard.db.is_invis


def teleport_to(wizard, target_room_or_char):
    """Instantly teleports wizard to destination."""
    dest = target_room_or_char if hasattr(target_room_or_char, "destination") or hasattr(target_room_or_char, "contents") else None
    if not dest and hasattr(target_room_or_char, "location"):
        dest = target_room_or_char.location

    if not dest:
        return False, "Invalid destination."

    old_loc = wizard.location
    wizard.move_to(dest, quiet=True)

    if old_loc and not getattr(wizard.db, "is_invis", False):
        old_loc.msg_contents(f"|m{wizard.key} vanishes in a flash of ethereal azure light.|n", exclude=[wizard])
    if dest and not getattr(wizard.db, "is_invis", False):
        dest.msg_contents(f"|m{wizard.key} steps out of an ethereal portal into the area.|n", exclude=[wizard])

    wizard.msg(f"|yTeleported to {dest.key}.|n")
    return True, "Teleported."


def summon_player(wizard, target_char):
    """Transports target player to wizard's current location."""
    if not wizard.location:
        return False, "You have no location."

    old_loc = target_char.location
    target_char.move_to(wizard.location, quiet=True)

    if old_loc:
        old_loc.msg_contents(f"|mA blinding celestial gateway opens and pulls {target_char.key} inward!|n", exclude=[target_char])
    wizard.location.msg_contents(f"|m{target_char.key} appears in a swirl of arcane starlight!|n", exclude=[target_char])

    target_char.msg(f"|Y*** SUMMONED! *** You have been transported to {wizard.key}'s presence!|n")
    wizard.msg(f"|ySummoned {target_char.key} to your location.|n")
    return True, "Summoned."

