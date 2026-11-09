"""
Nightmare LPmud Aviary Courier Pigeons & Skymail Engine.

Implements:
1. Homing Courier Pigeons with brass leg canisters.
2. Airborne message delivery across zones ('sendpigeon <target> <message>').
3. Delivered parchment letters and missives ('readletter').
4. Town Aviary and rooftop loft status ('pigeonloft').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def format_aviary_directory():
    """Formats the town aviary and pigeon loft status."""
    lines = [
        "|c" + "=" * 65 + "|n",
        "|w               PRAXIS ROOFTOP AVIARY & SKYMAIL LOFT               |n",
        "|c" + "=" * 65 + "|n",
        " |gBonded Courier Flock:|n 12 Grey Homing Pigeons (Active & Well-Fed)",
        " |yDelivery Speed:|n Swift Airborne Transit across All Realms",
        " |mHardware:|n Threaded Brass Leg Cylinders & Waterproof Waxed Parchment",
        "|c" + "-" * 65 + "|n",
        "|xTo dispatch a pigeon: 'sendpigeon <player> <message>'|n",
        "|c" + "=" * 65 + "|n"
    ]
    return "\n".join(lines)


def dispatch_courier_pigeon(caller, recipient_char, message=""):
    """Dispatches a homing pigeon carrying a message capsule to the recipient."""
    if not recipient_char:
        return False, "Specify who you wish to send a courier pigeon to."

    if not message:
        return False, "You must write a message to slip into the pigeon's leg canister!"

    # Create missive in recipient inventory
    letter = create_object(Object, key=f"Pigeon Missive from {caller.key}", location=recipient_char)
    letter.db.is_letter = True
    letter.db.sender = caller.key
    letter.db.body = message
    letter.db.desc = f"A tiny slip of parchment rolled into a brass cylinder, penned by {caller.key}."

    caller.msg(
        f"\n|Y[PIGEON DISPATCHED]|n You roll the parchment, seal it in a brass leg capsule,\n"
        f"and launch the grey homing pigeon into the air! It beats its wings, soaring toward |w{recipient_char.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} launches a swift courier pigeon carrying a sealed message cylinder into the sky.",
            exclude=[caller]
        )

    recipient_char.msg(
        f"\n|C*FLUTTER-FLUTTER!*|n A swift homing pigeon descends from the sky and lands on your shoulder!\n"
        f"It coos softly and presents a brass leg cylinder from |w{caller.key}|n!\n"
        f"|yUse 'readletter' to unroll the message!|n\n"
    )
    if recipient_char.location:
        recipient_char.location.msg_contents(
            f"A grey courier pigeon flutters down from above, landing softly upon {recipient_char.key}'s shoulder.",
            exclude=[recipient_char]
        )
    return True, "Pigeon delivered."


def read_pigeon_letter(caller, letter_name=""):
    """Reads a delivered parchment missive."""
    letter = None
    for obj in caller.contents:
        if getattr(obj.db, "is_letter", False):
            if not letter_name or letter_name.lower() in obj.key.lower():
                letter = obj
                break

    if not letter:
        return False, "You do not have any pigeon missives in your pack to read."

    sender = getattr(letter.db, "sender", "An Unknown Sender")
    body = getattr(letter.db, "body", "(The ink is smudged and unreadable.)")

    lines = [
        "|c" + "=" * 60 + "|n",
        f"|w                   COURIER SKYMAIL MISSIVE                    |n",
        "|c" + "=" * 60 + "|n",
        f" |ySender:|n |w{sender}|n",
        "|c" + "-" * 60 + "|n",
        f" |w\"{body}\"|n",
        "|c" + "=" * 60 + "|n"
    ]
    caller.msg("\n" + "\n".join(lines) + "\n")
    return True, "Letter read."

