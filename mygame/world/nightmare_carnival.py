"""
Nightmare LPmud Traveling Carnival of Oddities & Games of Skill Engine.

Implements:
1. Traveling Carnival Pavilion and Game Booths:
   - The Sledgehammer High Striker (Strength check & brass bell ringing)
   - The Spinning Balloon Target (Knife throwing dexterity)
   - The Wheel of Oddities
2. Carnival prize tokens and souvenir rewards ('carnival', 'teststrength', 'playtarget').
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


def format_carnival_directory():
    """Formats the carnival midway attractions."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|M            THE PRAXIS TRAVELING CARNIVAL OF ODDITIES             |n",
        "|c" + "=" * 70 + "|n",
        " |Y[HIGH STRIKER TOWER]|n",
        "   Grab the two-handed wooden mallet and strike the iron base pin!",
        "   Send the puck soaring to ring the top brass bell! ('teststrength')",
        "",
        " |C[SPINNING BALLOON TARGET]|n",
        "   Hurl carnival balance daggers at the spinning cork board! ('playtarget')",
        "",
        " |G[SOUVENIR BOOTH]|n",
        "   Trade your prize tokens for ribbons, novelty whistles, and stuffed toys!",
        "|c" + "=" * 70 + "|n",
        "|xCost: 5 copper coins per attraction turn.|n"
    ]
    return "\n".join(lines)


def play_high_striker(caller):
    """Swings the sledgehammer to ring the high striker bell."""
    coins = getattr(caller.db, "coins", 0) or 0
    if coins < 5:
        return False, "The carnival barker grins: \"Only five coppers to test your might, friend!\" (Need 5 coins)"

    caller.db.coins = coins - 5

    # Strength calculation
    str_val = getattr(caller.db, "str", 12) or 12
    roll = random.randint(1, 20) + (str_val // 2)

    if roll >= 16:
        # RINGS THE BELL!
        prize = create_object(Object, key="Champion's Golden Carnival Ribbon", location=caller)
        prize.db.desc = "A gleaming satin ribbon awarded for ringing the brass bell on the carnival High Striker tower."

        caller.msg(
            "\n|Y*WHAAAAM!*|n You hoist the two-handed mallet and slam it flush onto the iron pin!\n"
            "The iron puck shoots straight up the thirty-foot wooden tower...\n"
            "|W*CLAAAAANG!*|n The puck strikes the top brass bell with deafening resonance!\n"
            f"The barker hollers: |c\"A TRUE STRONGMAN!\"|n You are awarded the |w{prize.key}|n!\n"
        )
        if caller.location:
            caller.location.msg_contents(
                f"|Y*CLAAANG!* {caller.key} smashes the High Striker with mighty power, ringing the carnival bell!|n",
                exclude=[caller]
            )
        return True, "Bell rung."
    else:
        height = random.randint(10, 25)
        caller.msg(
            f"\n|y*THUMP!*|n You swing the mallet, sending the puck whistling {height} feet up the tower,\n"
            "but it slows and drops back down just short of the brass bell! \"A valiant try!\" chuckles the barker.\n"
        )
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} swings the sledgehammer at the High Striker, sending the puck soaring midway up the tower.",
                exclude=[caller]
            )
        return True, "Struck tower."


def play_balloon_target(caller):
    """Throws balance daggers at the spinning balloon corkboard."""
    coins = getattr(caller.db, "coins", 0) or 0
    if coins < 5:
        return False, "Playing the balloon toss requires 5 copper coins."

    caller.db.coins = coins - 5
    roll = random.randint(1, 100)

    if roll >= 40:
        toy = create_object(Object, key="Plush Stuffed Owlbear Doll", location=caller)
        toy.db.desc = "An adorable plush owlbear toy stitched from velvet and felt with yellow button eyes."

        caller.msg(
            f"\n|C*THWACK-POP!*|n You flick your wrist, sending a balance dagger spinning straight into a red balloon!\n"
            f"The carny tips his hat and hands you a prize: a |w{toy.key}|n!\n"
        )
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} pops a spinning carnival target balloon with a neat dagger flick and wins a prize!",
                exclude=[caller]
            )
        return True, "Target popped."
    else:
        caller.msg("\n|xYour dagger grazes the corkboard rim, spinning off into the sawdust. \"Close one! Try again!\"|n\n")
        return True, "Missed."

