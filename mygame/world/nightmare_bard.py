"""
Nightmare LPmud Bardic Songs, Instruments & Performance Engine.

Implements:
1. Musical instruments (Lutes, War Drums, Flutes).
2. Bardic songs and chants ('sing vitality', 'sing valor', 'sing lullaby').
3. Area party buffs (Stamina/HP recovery, damage bolsters, pacifying wild beasts).
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


SONGS = {
    "vitality": {
        "name": "Ballad of Vitality",
        "stamina_cost": 25,
        "desc": "A vibrant, uplifting melody that rejuvenates weary muscles and speeds healing.",
        "effect": "heal_allies"
    },
    "valor": {
        "name": "War Anthem of Valor",
        "stamina_cost": 25,
        "desc": "A thunderous rhythmic cadence that ignites heroic fervor and bolsters weapon strikes (+6 Damage).",
        "effect": "buff_damage"
    },
    "lullaby": {
        "name": "Lullaby of the Fey",
        "stamina_cost": 20,
        "desc": "An enchanting, hypnotic lullaby that pacifies wild animals and soothes anger.",
        "effect": "pacify"
    }
}


def play_instrument(caller, instrument):
    """Performs a melodic tune on an instrument."""
    caller.msg(f"\n|cYou cradle {instrument.key} and perform a dazzling, intricate melody!|n")
    if caller.location:
        caller.location.msg_contents(
            f"|c{caller.key} plays a beautiful, resonant tune upon {instrument.key}.|n",
            exclude=[caller]
        )
    return True, "Played."


def sing_bardic_song(caller, song_key):
    """Sings a magical bardic song, granting area buffs to allies."""
    key = song_key.lower().strip()
    song = SONGS.get(key)
    if not song:
        for s_k, data in SONGS.items():
            if key in s_k or key in data["name"].lower():
                song = data
                key = s_k
                break

    if not song:
        caller.msg(f"Unknown song '{song_key}'. Available: {', '.join(SONGS.keys())}")
        return False, "Unknown song."

    stamina = caller.db.stamina or 0
    cost = song["stamina_cost"]
    if stamina < cost:
        return False, f"You are too breathless to sing! (Requires {cost} Stamina)"

    caller.db.stamina -= cost
    loc = caller.location

    caller.msg(f"\n|Y*** BARDIC PERFORMANCE: {song['name'].upper()}! ***|n")
    caller.msg(f"|yYour voice rings out with melodic enchantment!|n\n")

    if loc:
        loc.msg_contents(
            f"|c{caller.key} raises their voice in song, filling the air with the enchanting strains of '{song['name']}'!|n",
            exclude=[caller]
        )

        allies = [o for o in loc.contents if hasattr(o, "db") and o.db.hp is not None and not getattr(o.db, "is_ghost", False)]

        if song["effect"] == "heal_allies":
            for ally in allies:
                ally.db.stamina = min(ally.db.max_stamina or 100, (ally.db.stamina or 0) + 30)
                ally.db.hp = min(ally.db.max_hp or 100, (ally.db.hp or 0) + 20)
                ally.msg(f"|gThe soothing ballad rejuvenates your body! (+30 Stamina, +20 HP)|n")

        elif song["effect"] == "buff_damage":
            for ally in allies:
                ally.db.valor_bonus = 6
                ally.msg(f"|YThe thundering war song fills your veins with fire! (+6 Melee Damage)|n")

        elif song["effect"] == "pacify":
            for obj in loc.contents:
                if getattr(obj.db, "is_beast", False) or "Wolf" in obj.key or "Bear" in obj.key:
                    obj.db.is_pacified = True
                    loc.msg_contents(f"|w{obj.key} yawns softly and curls peacefully onto the ground, enchanted by the song.|n")

    return True, "Song performed."

