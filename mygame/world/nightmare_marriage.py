"""
Nightmare LPmud Marriage, Wedding Rings & Spousal Telepathy System.

Implements:
1. Romantic proposals and matrimony ('propose <player>', 'accept proposal', 'marry').
2. Enchanted Gold Wedding Rings with spousal bindings.
3. Private cross-realm spousal telepathy channel ('ring <message>').
4. Vitals sensing and beacon guidance across the realm ('ring sense', 'ring beacon').
5. Legal divorce at the magistrate/chapel ('divorce').
"""

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.objects import Object

PENDING_PROPOSALS = {}


def create_wedding_ring(owner, spouse):
    """Spawns an enchanted wedding ring for a married adventurer."""
    ring = create_object(Object, key=f"Gold Wedding Ring ({spouse.key})", location=owner)
    ring.db.desc = f"A gleaming band of enchanted solid gold inscribed with the runes of eternal bond: 'Forever joined with {spouse.key}'."
    ring.db.is_wedding_ring = True
    ring.db.spouse_id = spouse.id
    ring.db.spouse_name = spouse.key
    ring.db.slot = "finger"
    ring.db.value = 250
    return ring


def propose_marriage(proposer, target):
    """Issues a formal marriage proposal."""
    if proposer == target:
        return False, "You cannot marry yourself!"

    if getattr(proposer.db, "spouse", None):
        return False, f"You are already married to {proposer.db.spouse}! You must divorce first."

    if getattr(target.db, "spouse", None):
        return False, f"{target.key} is already married to someone else!"

    PENDING_PROPOSALS[target.id] = proposer.id

    proposer.msg(f"\n|YYou get down on one knee and propose marriage to {target.key}!|n\n")
    target.msg(
        f"\n|Y*** MARRIAGE PROPOSAL! ***|n\n"
        f"|M{proposer.key} has dropped to one knee and asked for your hand in marriage!|n\n"
        f"To accept, type: |waccept proposal|n\n"
    )
    if proposer.location:
        proposer.location.msg_contents(
            f"|M{proposer.key} takes {target.key}'s hands and proposes marriage!|n",
            exclude=[proposer, target]
        )
    return True, "Proposal sent."


def officiate_marriage(proposer, target):
    """Binds two characters in matrimony, creating spousal rings."""
    proposer.db.spouse = target.key
    proposer.db.spouse_id = target.id
    target.db.spouse = proposer.key
    target.db.spouse_id = proposer.id

    create_wedding_ring(proposer, target)
    create_wedding_ring(target, proposer)

    proposer.msg(f"\n|M*** CONGRATULATIONS! *** You are now wed to {target.key}!|n")
    proposer.msg("|yYou slide the enchanted Gold Wedding Ring onto your finger! (Use: |wwring <msg>|y, |wring sense|y)|n\n")

    target.msg(f"\n|M*** CONGRATULATIONS! *** You are now wed to {proposer.key}!|n")
    target.msg("|yYou slide the enchanted Gold Wedding Ring onto your finger! (Use: |wwring <msg>|y, |wring sense|y)|n\n")

    if proposer.location:
        proposer.location.msg_contents(
            f"|YJoyous bells ring out! {proposer.key} and {target.key} are officially wed in holy matrimony!|n",
            exclude=[proposer, target]
        )
    return True, "Married."


def accept_proposal(target):
    """Accepts a pending marriage proposal."""
    proposer_id = PENDING_PROPOSALS.pop(target.id, None)
    if not proposer_id:
        return False, "You do not have any pending marriage proposals."

    proposer = ObjectDB.objects.filter(id=proposer_id).first()
    if not proposer:
        return False, "Your suitor is no longer online."

    return officiate_marriage(proposer, target)


def divorce_spouse(caller):
    """Dissolves the character's marriage."""
    spouse_id = getattr(caller.db, "spouse_id", None)
    spouse_name = getattr(caller.db, "spouse", "your spouse")

    if not spouse_id:
        return False, "You are not currently married."

    caller.db.spouse = None
    caller.db.spouse_id = None

    # Update spouse if online
    spouse = ObjectDB.objects.filter(id=spouse_id).first()
    if spouse:
        spouse.db.spouse = None
        spouse.db.spouse_id = None
        spouse.msg(f"\n|r[MARRIAGE DISSOLVED] {caller.key} has filed for divorce. You are now single.|n\n")

    caller.msg(f"\n|rYou have officially divorced {spouse_name}. The spousal bond is broken.|n\n")
    return True, "Divorced."


def ring_telepathy(caller, message):
    """Transmits a telepathic message directly through the wedding ring."""
    spouse_id = getattr(caller.db, "spouse_id", None)
    if not spouse_id:
        return False, "You are not married and bear no spousal wedding ring."

    spouse = ObjectDB.objects.filter(id=spouse_id).first()
    if not spouse:
        return False, f"Your spouse is currently wandering outside the physical realm (Offline)."

    caller.msg(f"|M[Ring Bond -> {spouse.key}] You whisper: \"{message}\"|n")
    spouse.msg(f"|M[Ring Bond <- {caller.key}] {caller.key} whispers: \"{message}\"|n")
    return True, "Message sent."


def ring_sense_spouse(caller):
    """Senses your spouse's location, realm, and vitals."""
    spouse_id = getattr(caller.db, "spouse_id", None)
    if not spouse_id:
        return False, "You are not married."

    spouse = ObjectDB.objects.filter(id=spouse_id).first()
    if not spouse:
        caller.msg(f"You focus on your wedding ring, but sense only quiet absence. ({caller.db.spouse} is offline).")
        return True, "Offline."

    loc_str = spouse.location.key if spouse.location else "The Ether"
    hp = spouse.db.hp or 0
    max_hp = spouse.db.max_hp or 100
    mana = spouse.db.mana or 0
    max_mana = spouse.db.max_mana or 100

    caller.msg(f"\n|M=== Spousal Bond: {spouse.key} ===|n")
    caller.msg(f"Location: |c{loc_str}|n")
    caller.msg(f"Vitals:   HP: |g{hp}/{max_hp}|n   Mana: |c{mana}/{max_mana}|n")
    if getattr(spouse.db, "is_ghost", False):
        caller.msg(f"State:    |r[GHOST - IN NEED OF RESURRECTION]|n")
    else:
        caller.msg(f"State:    |g[ALIVE]|n")
    caller.msg("|M" + "=" * 32 + "|n\n")
    return True, "Sensed."

