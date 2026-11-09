"""
Nightmare LPmud Clerical Undead Turning & Necromantic Thrall Binding.

Implements:
1. Cleric 'turn undead': Holy solar burst damaging and driving back undead.
2. Necromantic 'animate dead': Binds a soul into a fallen corpse, creating a fighting minion thrall.
3. Thrall command engine ('order thrall attack/guard/dismiss').
"""

import random
from evennia.utils.create import create_object
from typeclasses.characters import Character
from world.nightmare_core import start_combat, is_in_combat


def turn_undead(cleric, target=None):
    """
    Cleric channels celestial wrath to rebuke and destroy undead in the room.
    """
    if getattr(cleric.db, "is_ghost", False):
        return False, "You are a ghost and cannot channel celestial wrath."

    mana = cleric.db.mana or 0
    if mana < 25:
        return False, "You need at least 25 Mana to channel divine turning! (Requires 25 Mana)"

    cleric.db.mana -= 25

    loc = cleric.location
    if not loc:
        return False, "You are floating in the void."

    # Look for undead in the room
    undead_list = []
    if target:
        if getattr(target.db, "is_undead", False) or "Skeleton" in target.key or "Zombie" in target.key or "Ghoul" in target.key:
            undead_list.append(target)
    else:
        for obj in loc.contents:
            if obj != cleric and (getattr(obj.db, "is_undead", False) or "Skeleton" in obj.key or "Zombie" in obj.key or "Ghoul" in obj.key):
                undead_list.append(obj)

    cleric.msg("\n|Y*** SOLAR SMITE: TURN UNDEAD! ***|n")
    cleric.msg("|YYou thrust forward your holy symbol! Blinding, sanctified celestial fire bursts outward!|n")
    if loc:
        loc.msg_contents(
            f"|Y{cleric.key} raises a glowing holy symbol as brilliant solar radiance explodes across the room!|n",
            exclude=[cleric]
        )

    if not undead_list:
        cleric.msg("No unholy abominations or undead reside here to be turned.")
        return True, "No undead present."

    wis_bonus = (cleric.db.wis or 10) // 2
    for u in undead_list:
        dmg = random.randint(30, 60) + wis_bonus
        u.db.hp = max(0, (u.db.hp or 0) - dmg)
        cleric.msg(f"|YThe holy radiance scorches and chars {u.key} for {dmg} holy damage!|n")
        u.msg(f"|RRadiant celestial fire Sears your rotten bones for {dmg} damage!|n")

        if u.db.hp <= 0:
            cleric.msg(f"|w{u.key} dissolves into a harmless pile of purified ash!|n")
            u.delete()
        else:
            if not is_in_combat(cleric):
                start_combat(cleric, u)

    return True, "Turn complete."


def animate_dead(mage, corpse):
    """
    Necromantic incantation to reanimate a corpse into a skeletal thrall minion.
    """
    if getattr(mage.db, "is_ghost", False):
        return False, "You are a spirit and cannot perform physical necromancy."

    if not corpse or not corpse.key.lower().startswith("corpse"):
        return False, "You must target a fresh monster corpse to reanimate!"

    if getattr(corpse.db, "is_animated", False):
        return False, "This corpse's essence has already been drained."

    mana = mage.db.mana or 0
    if mana < 40:
        return False, "You need at least 40 Mana to animate the dead! (Requires 40 Mana)"

    mage.db.mana -= 40
    corpse_name = corpse.key.replace("Corpse of ", "").strip()
    corpse.delete()

    loc = mage.location

    # Create Minion Thrall
    thrall = create_object(Character, key=f"Skeletal Thrall of {mage.key}", location=loc)
    thrall.db.desc = f"An animate skeleton composed of blackened bone and clattering sinew, raised from a {corpse_name}. Pale unholy flames flicker inside its eye sockets."
    thrall.db.is_undead = True
    thrall.db.is_thrall = True
    thrall.db.master_id = mage.id
    thrall.db.hp = 65
    thrall.db.max_hp = 65
    thrall.db.damage_bonus = 6

    mage.db.active_thrall = thrall

    mage.msg(f"\n|m*** NECROMANTIC AWAKENING! ***|n")
    mage.msg(f"|mYou chant the dark incantation 'Mors Resurget!' Black spectral lightning courses through {corpse_name}!|n")
    mage.msg(f"|wThe bones knit together and rise: |c{thrall.key}|w stands ready to serve!|n\n")

    if loc:
        loc.msg_contents(
            f"|m{mage.key} channels unholy shadow into the ground! The bones of {corpse_name} rattle and assemble into {thrall.key}!|n",
            exclude=[mage]
        )
    return True, "Animated dead."


def order_thrall(master, command_text):
    """Issues orders to your active skeletal thrall."""
    thrall = getattr(master.db, "active_thrall", None)
    if not thrall or not thrall.pk:
        return False, "You do not have an active summoned thrall."

    cmd = command_text.strip().lower()

    if cmd == "dismiss":
        master.msg(f"|mYou release the dark binding tether. {thrall.key} collapses into a pile of lifeless bone.|n")
        thrall.delete()
        master.db.active_thrall = None
        return True, "Thrall dismissed."

    elif cmd.startswith("attack"):
        target_name = cmd.replace("attack", "").strip()
        target = master.search(target_name, location=master.location)
        if not target:
            return False, "Attack who?"

        master.msg(f"|mYou command your thrall to attack {target.key}!|n")
        start_combat(thrall, target)
        return True, "Attacking."

    elif cmd == "guard":
        master.msg(f"|mYour skeletal thrall assumes a defensive stance beside you.|n")
        return True, "Guarding."

    else:
        return False, "Available thrall orders: |worder thrall attack <target>|n, |worder thrall guard|n, |worder thrall dismiss|n."

