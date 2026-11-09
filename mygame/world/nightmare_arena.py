"""
Nightmare LPmud Grand Arena, Sanctioned Duels & Gladiator Wagers.

Implements:
1. Formal duel challenges ('duel challenge <player> [wager_gold]').
2. Dual arena ring teleportation and combat initiation ('duel accept').
3. Non-lethal resolution (yielding at low health without true death or ghosting).
4. Gold wager payouts and Gladiator Honor rating progression.
"""

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room

ARENA_RING_KEY = "Sigil Grand Colosseum - The Blood Sands"
SPECTATOR_STANDS_KEY = "Sigil Grand Colosseum - Imperial Balcony"

# Active pending challenges: {target_id: {"challenger_id": int, "wager": int}}
PENDING_DUELS = {}


def get_or_create_arena_ring():
    """Retrieves or spawns the combat arena ring."""
    ring = ObjectDB.objects.filter(db_key=ARENA_RING_KEY).first()
    if not ring:
        ring = create_object(
            Room,
            key=ARENA_RING_KEY,
            attributes=[
                ("desc", "A vast circular sand arena enclosed by high granite battlements and iron spikes. Banners of legendary champions flutter above the roar of the crowd."),
                ("terrain", "dungeon"),
                ("is_arena", True)
            ]
        )
    return ring


def get_or_create_spectator_stands():
    """Retrieves or spawns the spectator balcony."""
    stands = ObjectDB.objects.filter(db_key=SPECTATOR_STANDS_KEY).first()
    if not stands:
        stands = create_object(
            Room,
            key=SPECTATOR_STANDS_KEY,
            attributes=[
                ("desc", "A high canopied marble terrace overlooking the arena sands below. Spectators sip wine and cheer as gladiators clash."),
                ("terrain", "city"),
                ("is_spectator", True)
            ]
        )
    return stands


def challenge_duel(challenger, target, wager=0):
    """Issues a formal duel challenge with optional gold wager."""
    if challenger == target:
        return False, "You cannot duel yourself!"

    if getattr(challenger.db, "is_ghost", False) or getattr(target.db, "is_ghost", False):
        return False, "Ghosts cannot participate in sanctioned arena duels."

    if wager > 0:
        c_gold = (challenger.db.coins or {}).get("gold", 0)
        t_gold = (target.db.coins or {}).get("gold", 0)
        if c_gold < wager:
            return False, f"You do not have {wager} Gold for this wager."
        if t_gold < wager:
            return False, f"{target.key} does not have {wager} Gold to match your wager."

    PENDING_DUELS[target.id] = {
        "challenger_id": challenger.id,
        "challenger_name": challenger.key,
        "wager": wager
    }

    challenger.msg(f"\n|Y[DUEL CHALLENGE SENT]|n You have challenged {target.key} to an honor duel (Wager: {wager} Gold)!\n")
    target.msg(
        f"\n|Y*** DUEL CHALLENGE! ***|n\n"
        f"{challenger.key} has challenged you to an arena duel for |y{wager} Gold|n!\n"
        f"Type |wduel accept|n to enter the arena, or ignore to decline.\n"
    )
    return True, "Challenge issued."


def accept_duel(target):
    """Accepts a pending duel challenge, transporting fighters to the arena."""
    from world.nightmare_core import start_combat

    challenge = PENDING_DUELS.pop(target.id, None)
    if not challenge:
        return False, "You have no active duel challenges to accept."

    challenger_id = challenge["challenger_id"]
    challenger = ObjectDB.objects.filter(id=challenger_id).first()
    if not challenger:
        return False, "Challenger is no longer online."

    wager = challenge["wager"]
    arena = get_or_create_arena_ring()

    # Move both to arena
    challenger.move_to(arena, quiet=True)
    target.move_to(arena, quiet=True)

    challenger.db.pre_duel_hp = challenger.db.hp
    target.db.pre_duel_hp = target.db.hp
    challenger.db.active_duel = {"opponent_id": target.id, "wager": wager}
    target.db.active_duel = {"opponent_id": challenger.id, "wager": wager}

    arena.msg_contents(
        f"\n|Y========================== ARENA DUEL COMMENCES! ==========================|n\n"
        f"|W{challenger.key} and {target.key} step onto the blood sands!|n\n"
        f"|yWager at stake: {wager} Gold! Sound the war horns!|n\n"
        f"|Y===========================================================================|n\n"
    )

    # Engage combat
    start_combat(challenger, target)
    return True, "Duel started."


def conclude_duel(victor, loser):
    """Resolves the duel cleanly without death, awarding wagers and rating."""
    from world.nightmare_core import disengage_combat

    duel_data = getattr(victor.db, "active_duel", {}) or {}
    wager = duel_data.get("wager", 0)

    victor.db.active_duel = None
    loser.db.active_duel = None

    disengage_combat(victor, loser)

    # Wager transfer
    if wager > 0:
        l_coins = loser.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        v_coins = victor.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        actual_wager = min(l_coins.get("gold", 0), wager)
        l_coins["gold"] -= actual_wager
        v_coins["gold"] = v_coins.get("gold", 0) + actual_wager
        loser.db.coins = l_coins
        victor.db.coins = v_coins

    # Gladiator Rating
    victor.db.gladiator_rating = (victor.db.gladiator_rating or 1000) + 25
    loser.db.gladiator_rating = max(800, (loser.db.gladiator_rating or 1000) - 15)

    # Restores minimal health so loser doesn't bleed out
    loser.db.hp = max(10, loser.db.hp or 10)

    msg = (
        f"\n|Y*** DUEL VICTORY! ***|n\n"
        f"|W{loser.key} yields with honor before {victor.key}!|n\n"
        f"|G{victor.key} is declared Champion of the Sands! (+25 Gladiator Rating)|n\n"
    )
    if wager > 0:
        msg += f"|y{victor.key} collects the {wager} Gold wager!|n\n"

    arena = victor.location
    if arena:
        arena.msg_contents(msg)

    return True, "Duel concluded."

