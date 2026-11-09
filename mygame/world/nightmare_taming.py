"""
Nightmare LPmud Beast Taming & Animal Companion Engine.

Implements:
1. Taming wild beasts with raw meat rations ('tame <beast> with <meat>').
2. Loyal animal companions following their master into battle.
3. Companion orders ('pet attack <target>', 'pet stay', 'pet heel').
4. Companion feeding and health maintenance.
"""

from evennia.utils.create import create_object
from typeclasses.characters import Character
from world.nightmare_core import start_combat


def tame_wild_beast(caller, beast, meat_item):
    """Tames a wild beast into a loyal bonded animal companion."""
    if not getattr(beast.db, "is_beast", False) and "Wolf" not in beast.key and "Hound" not in beast.key and "Hawk" not in beast.key and "Bear" not in beast.key:
        return False, f"{beast.key} cannot be tamed into an animal companion!"

    if getattr(beast.db, "is_companion", False):
        return False, f"{beast.key} is already bonded to a master."

    if getattr(caller.db, "active_companion", None):
        return False, "You already have an active bonded animal companion!"

    meat_item.delete()

    beast.db.is_companion = True
    beast.db.owner_id = caller.id
    beast.db.owner_name = caller.key
    caller.db.active_companion = beast

    caller.msg(f"\n|Y[BEAST TAMED]|n You offer meat and speak soothing words. {beast.key} sniffs your hand, then nuzzles you affectionately!")
    caller.msg(f"|G{beast.key} is now your loyal animal companion! (Use: |wpet attack <target>|G, |wpet stay|G, |wpet heel|G)|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"{beast.key} bonds with {caller.key}, accepting them as their master.",
            exclude=[caller]
        )
    return True, "Tamed."


def order_companion(master, command_text):
    """Issues tactical orders to your active bonded animal companion."""
    pet = getattr(master.db, "active_companion", None)
    if not pet or not pet.pk:
        return False, "You do not have an active animal companion."

    cmd = command_text.strip().lower()

    if cmd.startswith("attack"):
        target_name = cmd.replace("attack", "").strip()
        target = master.search(target_name, location=master.location)
        if not target:
            return False, "Attack who?"

        master.msg(f"|rYou point forward and command {pet.key} to attack {target.key}!|n")
        start_combat(pet, target)
        return True, "Attacking."

    elif cmd in ["heel", "follow"]:
        pet.move_to(master.location, quiet=True)
        master.msg(f"|g{pet.key} trotting obediently at your heel.|n")
        return True, "Heeling."

    elif cmd == "stay":
        master.msg(f"|yYou command {pet.key} to stay and watch over this area.|n")
        return True, "Staying."

    elif cmd == "release":
        master.db.active_companion = None
        pet.db.is_companion = False
        pet.db.owner_id = None
        master.msg(f"|yYou unfasten the collar and release {pet.key} back into the wild.|n")
        return True, "Released."

    else:
        return False, "Available orders: |wpet attack <target>|n, |wpet heel|n, |wpet stay|n, |wpet release|n."


def feed_companion(master, pet, meat_item):
    """Feeds companion meat to restore HP and bolster bond."""
    pet.db.hp = min(pet.db.max_hp or 80, (pet.db.hp or 0) + 35)
    meat_name = meat_item.key
    meat_item.delete()

    master.msg(f"\n|gYou feed {meat_name} to {pet.key}. It wolfs it down with joyful tail-wagging! (+35 HP)|n\n")
    return True, "Fed."

