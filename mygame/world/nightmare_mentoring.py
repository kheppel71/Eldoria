"""
Nightmare LPmud Player Mentoring, Novice Channel & Guide Engine.

Implements:
1. Realm Guide registration ('guide') for veteran players.
2. Global Novice Channel ('newbie <msg>').
3. Tutoring partnerships ('tutor <novice>') granting +15% shared XP.
"""

from evennia.objects.models import ObjectDB

REGISTERED_GUIDES = set()


def register_as_guide(caller):
    """Registers a veteran player as an active realm guide."""
    lvl = caller.db.level or 1
    if lvl < 5:
        return False, "You must be at least Level 5 to register as an official Realm Guide!"

    is_g = getattr(caller.db, "is_guide", False)
    caller.db.is_guide = not is_g

    if caller.db.is_guide:
        REGISTERED_GUIDES.add(caller.id)
        caller.msg("\n|Y[REALM GUIDE REGISTERED]|n You have enlisted as an official Realm Guide!")
        caller.msg("Novice adventurers will see your guide honors. Answer questions on the |wnewbie|n channel!\n")
    else:
        REGISTERED_GUIDES.discard(caller.id)
        caller.msg("\n|yYou have stepped down from active Realm Guide duties.|n\n")

    return True, "Toggled."


def broadcast_newbie_channel(caller, message):
    """Broadcasts a question or advice across the global newbie channel."""
    is_guide = getattr(caller.db, "is_guide", False)
    tag = f"|G[Guide {caller.key}]|n" if is_guide else f"|y[Novice {caller.key}]|n"

    formatted_msg = f"{tag}: {message.strip()}"

    # Broadcast to all online players
    for char in ObjectDB.objects.filter(db_typeclass_path__contains="characters"):
        if hasattr(char, "msg") and char.sessions.all():
            char.msg(formatted_msg)

    return True, "Broadcast."


def establish_tutoring(mentor, student):
    """Binds mentor and student into a tutoring partnership."""
    if mentor == student:
        return False, "You cannot tutor yourself!"

    m_lvl = mentor.db.level or 1
    s_lvl = student.db.level or 1

    if m_lvl <= s_lvl:
        return False, f"You must be higher level than {student.key} to tutor them!"

    mentor.db.tutee_id = student.id
    student.db.mentor_id = mentor.id

    mentor.msg(f"\n|Y[TUTORING BOND]|n You take {student.key} under your wing as your apprentice!")
    mentor.msg("|GBoth of you earn +15% bonus Experience Points when adventuring together!|n\n")

    student.msg(f"\n|Y[TUTORING BOND]|n {mentor.key} has taken you under their wing as their apprentice!")
    student.msg("|GYou will earn +15% bonus Experience Points when adventuring together!|n\n")

    return True, "Tutored."

