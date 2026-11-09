"""
Nightmare LPmud Justice, Law Enforcement, Jail & Bounty System.

Implements:
1. Outlaw & Criminal Tracking:
   - Assaulting innocents, unprovoked PK, or theft flags players as Outlaws.
   - Crimes log with timestamps and bounty accumulations.
2. The City Watch & Praetor Arrest AI:
   - City guards scan rooms for Outlaws.
   - Guards demand surrender or engage in combat.
   - Defeating or subduing an outlaw teleports them to the city stockade/jail.
3. Jail & Sentence System:
   - Barred jail cell mechanics with sentence countdowns.
   - Surrender command ('surrender') to yield to guards peacefully.
   - Bail system: pay the magistrate/bailiff to release prisoners early.
4. Realm Bounty Board:
   - 'bounties': view current most-wanted outlaws and rewards.
   - 'bounty place <player> <gold>': post a reward on a criminal.
   - 'bounty claim <player>': claim reward upon defeating/arresting the wanted criminal.
"""

import time
from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room

# In-memory realm bounties cache: {char_id: {"name": str, "bounty": int, "crimes": list}}
BOUNTIES = {}

JAIL_CELL_KEY = "Sigil Hive Ward Stockade"
COURTHOUSE_KEY = "Sigil Hall of Justice"


def init_justice_character(char):
    """Initializes justice-related attributes on a character."""
    if not hasattr(char, "db"):
        return
    if char.db.is_outlaw is None:
        char.db.is_outlaw = False
    if char.db.bounty is None:
        char.db.bounty = 0
    if char.db.crimes is None:
        char.db.crimes = []
    if char.db.jail_time is None:
        char.db.jail_time = 0
    if char.db.is_jailed is None:
        char.db.is_jailed = False


def record_crime(criminal, crime_type, victim=None, bounty_add=50):
    """
    Records a crime committed by criminal, flags them as an outlaw,
    and places or increases a bounty on their head.
    """
    init_justice_character(criminal)
    criminal.db.is_outlaw = True
    new_bounty = (criminal.db.bounty or 0) + bounty_add
    criminal.db.bounty = new_bounty

    crime_entry = {
        "crime": crime_type,
        "victim": victim.key if victim else "Citizens of Sigil",
        "time": time.time(),
        "bounty": bounty_add
    }
    crimes = criminal.db.crimes or []
    crimes.append(crime_entry)
    criminal.db.crimes = crimes

    BOUNTIES[criminal.id] = {
        "name": criminal.key,
        "bounty": new_bounty,
        "crimes": [c["crime"] for c in crimes[-3:]]
    }

    criminal.msg(f"\n|r[CRIMINAL ACT] You have committed {crime_type}!|n")
    criminal.msg(f"|RYou are now an OUTLAW of the realm! Bounty: {new_bounty} Gold.|n\n")

    if criminal.location:
        criminal.location.msg_contents(
            f"|rAn alarm sounds! {criminal.key} has been branded an OUTLAW for {crime_type}!|n",
            exclude=[criminal]
        )


def get_or_create_jail():
    """Finds or creates the central jail cell for criminals."""
    cell = ObjectDB.objects.filter(db_key=JAIL_CELL_KEY).first()
    if not cell:
        cell = create_object(
            Room,
            key=JAIL_CELL_KEY,
            attributes=[
                ("desc", "Cold iron bars and damp, dripping stone form this grim dungeon cell. A heavy, iron-reinforced oak door is bolted from the outside. The only light trickles through a slit in the masonry."),
                ("terrain", "dungeon"),
                ("is_jail", True)
            ]
        )
    return cell


def get_or_create_courthouse():
    """Finds or creates the courthouse / release area."""
    court = ObjectDB.objects.filter(db_key=COURTHOUSE_KEY).first()
    if not court:
        court = create_object(
            Room,
            key=COURTHOUSE_KEY,
            attributes=[
                ("desc", "High vaulted marble arches and scales of justice overlook the magistrates' benches. Clerks and bailiffs maintain the law and order of the realm."),
                ("terrain", "city"),
                ("is_courthouse", True)
            ]
        )
    return court


def arrest_criminal(officer, criminal, sentence_seconds=60):
    """
    Arrests an outlaw and transfers them to the central stockade.
    """
    from world.nightmare_core import disengage_combat

    init_justice_character(criminal)
    disengage_combat(criminal)
    if officer:
        disengage_combat(officer)

    jail = get_or_create_jail()
    criminal.db.pre_jail_loc = criminal.location
    criminal.db.is_jailed = True
    criminal.db.jail_time = sentence_seconds

    if criminal.location:
        criminal.location.msg_contents(
            f"|yThe City Watch claps heavy iron manacles on {criminal.key} and drags them away to the stockades!|n",
            exclude=[criminal]
        )

    criminal.move_to(jail, quiet=True)
    criminal.msg(
        f"\n|r*** UNDER ARREST! ***|n\n"
        f"You are thrown into {jail.key}!\n"
        f"Your sentence is {sentence_seconds} seconds.\n"
        f"Use |wserve|n to wait out your sentence or have an ally pay your bail at the magistrate.\n"
    )


def release_prisoner(criminal, pardon=False):
    """Releases a prisoner from jail after sentence expires or bail is paid."""
    init_justice_character(criminal)
    court = get_or_create_courthouse()
    criminal.db.is_jailed = False
    criminal.db.jail_time = 0

    if pardon:
        criminal.db.is_outlaw = False
        criminal.db.bounty = 0
        BOUNTIES.pop(criminal.id, None)

    criminal.move_to(court, quiet=True)
    criminal.msg(
        f"\n|gThe stockade gate swings open! You are escorted to {court.key} and released.|n\n"
    )
    if court:
        court.msg_contents(
            f"The bailiff escorts {criminal.key} into the courthouse, now released from custody.",
            exclude=[criminal]
        )


def pay_bail(caller, criminal):
    """Pays bail for a jailed criminal."""
    init_justice_character(criminal)
    if not criminal.db.is_jailed:
        return False, f"{criminal.key} is not currently incarcerated."

    # Bail cost scales with remaining bounty and sentence
    bounty = criminal.db.bounty or 50
    bail_cost = max(50, bounty // 2)

    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    if coins.get("gold", 0) < bail_cost:
        return False, f"You need {bail_cost} Gold to post bail for {criminal.key} (You have {coins.get('gold', 0)} Gold)."

    coins["gold"] -= bail_cost
    caller.db.coins = coins

    release_prisoner(criminal, pardon=True)
    return True, f"You paid {bail_cost} Gold in bail for {criminal.key}! They have been released and pardoned."


def place_bounty(placer, target, amount):
    """Allows a player or authority to place a gold bounty on an outlaw."""
    init_justice_character(target)
    if not target.db.is_outlaw:
        return False, f"{target.key} is not an outlaw! Bounties can only be placed on criminals."

    coins = placer.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    if coins.get("gold", 0) < amount:
        return False, f"You do not have {amount} Gold to post on a bounty."

    coins["gold"] -= amount
    placer.db.coins = coins

    target.db.bounty = (target.db.bounty or 0) + amount
    b_data = BOUNTIES.setdefault(target.id, {"name": target.key, "bounty": 0, "crimes": []})
    b_data["bounty"] += amount
    b_data["name"] = target.key

    return True, f"You placed a {amount} Gold bounty on {target.key}! (Total Bounty: {b_data['bounty']} Gold)"


def claim_bounty(hunter, target):
    """Awards the posted bounty to the hunter after subduing the outlaw."""
    init_justice_character(target)
    bounty = target.db.bounty or 0
    if bounty <= 0:
        return False, f"There is no active bounty on {target.key}."

    coins = hunter.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    coins["gold"] = coins.get("gold", 0) + bounty
    hunter.db.coins = coins

    target.db.bounty = 0
    BOUNTIES.pop(target.id, None)

    hunter.msg(f"|Y[BOUNTY COLLECTED] You receive {bounty} Gold for bringing {target.key} to justice!|n")
    return True, f"Bounty of {bounty} Gold claimed successfully!"

