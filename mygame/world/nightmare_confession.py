"""
Nightmare LPmud Cathedral Confessionals, Penance & Absolution Engine.

Implements:
1. Mahogany Cathedral Confessional Booths.
2. Sin Confession to the High Confessor ('confess <misdeed>').
3. Holy Penance fulfillment ('performpenance').
4. Divine Absolution blessings ('absolve').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def enter_confession(caller, sin_description=""):
    """Kneels behind the latticed screen to confess sins."""
    if not sin_description:
        return False, "What moral transgression or burden do you wish to confess to the holy confessor?"

    caller.db.active_penance = {
        "sin": sin_description,
        "penance_cost": 25,
        "penance_fulfilled": False
    }

    caller.msg(
        f"\n|W[SACRED CONFESSIONAL]|n You kneel upon the velvet kneeler behind the carved wooden lattice.\n"
        f"You whisper: |w\"{sin_description}\"|n\n\n"
        "The High Confessor's gentle voice whispers through the screen:\n"
        "|c\"The heavens hear your remorse, child. Your penance is to offer twenty-five gold coins\n"
        "to the temple alms coffer for the poor ('performpenance'). Only then may you receive absolution.\"|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} kneels reverently within the carved wooden confessional booth.",
            exclude=[caller]
        )
    return True, "Confession recorded."


def perform_holy_penance(caller):
    """Offers donation or sacred prayers to fulfill the assigned penance."""
    penance = getattr(caller.db, "active_penance", None)
    if not penance:
        return False, "You have not confessed any transgressions requiring penance! ('confess <sin>')"

    if penance.get("penance_fulfilled", False):
        return False, "Your penance has already been fulfilled! Seek the priest for holy absolution ('absolve')."

    cost = penance["penance_cost"]
    coins = getattr(caller.db, "coins", 0) or 0

    if coins < cost:
        return False, f"Your assigned penance requires {cost} gold coins for the poor's alms coffer (you have {coins})."

    caller.db.coins = coins - cost
    penance["penance_fulfilled"] = True
    caller.db.active_penance = penance

    caller.msg(
        f"\n|Y[PENANCE FULFILLED]|n You place {cost} gold coins into the temple alms chest and bow your head in prayer.\n"
        "A peaceful warmth touches your spirit. You are ready for holy absolution ('absolve')!\n"
    )
    return True, "Penance fulfilled."


def receive_divine_absolution(caller):
    """Receives the priest's blessing and divine absolution."""
    penance = getattr(caller.db, "active_penance", None)
    if not penance or not penance.get("penance_fulfilled", False):
        return False, "You cannot be absolved until your sacred penance has been performed! ('performpenance')"

    caller.db.active_penance = None
    caller.db.holy_absolution_buff = True

    caller.msg(
        "\n|W[DIVINE ABSOLUTION]|n The High Confessor steps from the booth and places consecrated hands upon your head:\n"
        "|c\"Ego te absolvo in nomine caeli. Go forth unburdened, cleansed in the light.\"|n\n"
        "|GGolden radiance descends upon you! You receive the |W'Holy Absolution'|G blessing! (+Divine Favor)|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"|WGolden celestial radiance washes over {caller.key} as the High Confessor imparts sacred absolution!|n",
            exclude=[caller]
        )
    return True, "Absolved."

