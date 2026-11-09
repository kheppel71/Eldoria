"""
Nightmare LPmud Tavern Dice Gambling & Dragon's Hazard System.

Implements:
1. High-stakes dice wagering against the house ('dice roll <wager>').
2. Authentic classic Hazard rules (naturals on 7/11, craps on 2/3/12).
3. Payouts and coin purse updates.
"""

import random


def play_dice_hazard(caller, wager_gold=5):
    """Executes a round of Dragon's Hazard dice betting against the house."""
    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    if coins.get("gold", 0) < wager_gold:
        return False, f"You need {wager_gold} Gold to make that wager (You have {coins.get('gold', 0)} Gold)."

    # Roll player dice (2d6)
    p1 = random.randint(1, 6)
    p2 = random.randint(1, 6)
    p_total = p1 + p2

    caller.msg(f"\n|Y[DRAGON'S HAZARD]|n You shake the polished bone dice and toss them across the wooden tavern table...")
    caller.msg(f"|yYour dice land: [ {p1} ] and [ {p2} ] -> Total: |w{p_total}|y!|n")

    if p_total in [7, 11]:
        # Natural win!
        payout = wager_gold * 2
        coins["gold"] += (payout - wager_gold)
        caller.db.coins = coins
        caller.msg(f"\n|G*** NATURAL WINNER! *** A lucky {p_total}! You win {payout} Gold!|n\n")
        if caller.location:
            caller.location.msg_contents(
                f"|G{caller.key} rolls a natural {p_total} in dice and sweeps a pile of {payout} Gold off the table!|n",
                exclude=[caller]
            )
        return True, "Natural win."

    elif p_total in [2, 3, 12]:
        # Craps! House wins
        coins["gold"] -= wager_gold
        caller.db.coins = coins
        caller.msg(f"\n|R*** CRAPS! *** An unlucky roll of {p_total}! The house takes your {wager_gold} Gold.|n\n")
        if caller.location:
            caller.location.msg_contents(
                f"|r{caller.key} groans as they roll {p_total} in dice and lose {wager_gold} Gold!|n",
                exclude=[caller]
            )
        return True, "Craps loss."

    else:
        # House rolls against player
        h1 = random.randint(1, 6)
        h2 = random.randint(1, 6)
        h_total = h1 + h2
        caller.msg(f"|yThe tavern house rolls: [ {h1} ] and [ {h2} ] -> Total: |w{h_total}|y!|n")

        if p_total > h_total:
            payout = wager_gold * 2
            coins["gold"] += (payout - wager_gold)
            caller.db.coins = coins
            caller.msg(f"\n|G*** VICTORY! *** Your {p_total} beats the house's {h_total}! You win {payout} Gold!|n\n")
            return True, "Win."
        elif p_total < h_total:
            coins["gold"] -= wager_gold
            caller.db.coins = coins
            caller.msg(f"\n|r*** DEFEAT! *** The house's {h_total} edges out your {p_total}. You forfeit {wager_gold} Gold.|n\n")
            return True, "Loss."
        else:
            caller.msg(f"\n|w*** PUSH! *** Both rolled {p_total}! Bets are returned.|n\n")
            return True, "Push."

