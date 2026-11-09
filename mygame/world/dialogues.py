"""
Interactive EvMenu dialogue trees for Eldoria NPCs.
Comprehensive quest lines for all 10 mini-quests across Eldoria.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


# =============================================================================
# 1. BARNABY THE BARKEEP (The Drunken Dragon Tavern)
# =============================================================================

def barnaby_start_node(caller):
    text = (
        "|cBarnaby the Barkeep|n wipes down the polished oak bar with a damp rag "
        "and flashes you a warm, toothy grin.\n\n"
        "\"Welcome to the Drunken Dragon, traveler! Best spiced mead and roast boar "
        "in all of Eldoria. What can I get for you today?\""
    )
    options = (
        {"desc": "Pour me a hearty dwarven stout! (On the house)", "goto": "barnaby_drink"},
        {"desc": "Heard any interesting rumors around town lately?", "goto": "barnaby_rumors"},
        {"desc": "Do you know anyone in Eldoria in need of an adventurer's help?", "goto": "barnaby_quests"},
        {"desc": "Just looking around. Thanks, Barnaby.", "goto": "barnaby_farewell"},
    )
    return text, options


def barnaby_drink(caller):
    stout = create_object(
        Object,
        key="Frothing Tankard of Stout",
        location=caller,
        aliases=["tankard", "stout", "beer", "ale"],
        tags=["eldoria_world"]
    )
    stout.db.desc = "A heavy wooden tankard filled to the brim with dark, malty dwarven stout topped with thick foam."
    stout.db.is_drinkable = True
    stout.db.drink_type = "stout"

    text = (
        "Barnaby reaches under the counter, pulls a wooden tankard, and fills it from a "
        "foaming copper tap.\n\n"
        "\"Here you go, friend! First one is on the house for weary travelers. "
        "Drink it whenever you need your spirits lifted!\""
    )
    options = (
        {"desc": "Thanks! Can I ask you about something else?", "goto": "barnaby_start_node"},
        {"desc": "Much appreciated! (Step away)", "goto": None}
    )
    return text, options


def barnaby_rumors(caller):
    text = (
        "Barnaby leans in close and lowers his voice to a conspiratorial whisper:\n\n"
        "\"Well, if you're asking... our wine cellar down below has had a strange, cold draft "
        "whispering through the stone foundation lately. The old salts down at the harbor whisper "
        "that ancient smugglers built a secret passageway connecting the cellar right into the Old Salt Warehouse! "
        "I haven't had the courage to dig behind the casks myself.\n\n"
        "And worse yet... hunters from the Whispering Woods say goblins have taken root up in the craggy foothills "
        "near the old Hollow Gate. Keep your blade sharp if you travel north!\""
    )
    options = (
        {"desc": "Fascinating. Let's talk about something else.", "goto": "barnaby_start_node"},
        {"desc": "I'll keep my eyes open. Farewell.", "goto": None}
    )
    return text, options


def barnaby_quests(caller):
    text = (
        "\"Aye! Lots of folk are looking for help:\n\n"
        "- |wTobin|n at the Blacksmith dropped an important mechanical gear in the plaza fountain.\n"
        "- |wSister Meredith|n at the Cathedral is heartbroken over a stolen gilded chalice.\n"
        "- |wSilas|n at the harbor looks terrified about something happening in the warehouse.\n"
        "- |wMadam Belladonna|n at the apothecary needs glowing swamp moss from the mire.\n"
        "- |wLord Commander Valerius|n has posted bounties on the goblin chief and the Hollow King!\""
    )
    options = (
        {"desc": "Good to know. Back to what we were saying...", "goto": "barnaby_start_node"},
        {"desc": "Time to seek them out. Goodbye, Barnaby.", "goto": None}
    )
    return text, options


def barnaby_farewell(caller):
    return "\"Safe travels, friend! Stop back whenever your throat is parched!\"", None


# =============================================================================
# 2. MADAM BELLADONNA (The Silver Crucible Apothecary)
# =============================================================================

def belladonna_start_node(caller):
    has_quest = caller.db.belladonna_quest_active
    completed = caller.db.completed_belladonna_quest

    text = (
        "|cMadam Belladonna|n looks up from her brass balance scale, wiping her delicate "
        "hands on a velvet apron. A spiral of violet, cinnamon-scented smoke drifts lazily from an alembic.\n\n"
        "\"Welcome, seeker of remedies. The mysteries of root, herb, and crystal are open to those who respect nature's craft.\""
    )

    options = [
        {"desc": "What kind of wares and remedies do you brew here?", "goto": "belladonna_wares"},
    ]

    if not has_quest and not completed:
        options.append({
            "desc": "Do you need any assistance or rare ingredients gathered?",
            "goto": "belladonna_quest_offer"
        })
    elif has_quest and not completed:
        options.append({
            "desc": "I have gathered the Luminous Swamp Moss for you! [Turn in Quest]",
            "goto": "belladonna_quest_turnin"
        })
    elif completed:
        options.append({
            "desc": "Any more work needed after the swamp moss?",
            "goto": "belladonna_quest_aftermath"
        })

    options.append({"desc": "Farewell, Madam Belladonna.", "goto": "belladonna_farewell"})
    return text, tuple(options)


def belladonna_wares(caller):
    text = (
        "Belladonna sweeps her hand across shelves lined with glowing phials.\n\n"
        "\"I brew restorative draughts capable of knitting broken bone and soothing fevered minds. "
        "My crowning creation is the Glowing Health Elixir—one draught will revitalize any wounded adventurer!\""
    )
    options = (
        {"desc": "Let's discuss something else.", "goto": "belladonna_start_node"},
        {"desc": "Good to know. Farewell.", "goto": None}
    )
    return text, options


def belladonna_quest_offer(caller):
    caller.db.belladonna_quest_active = True
    text = (
        "Her amber eyes illuminate with sudden excitement.\n\n"
        "\"As a matter of fact, yes! I am in dire need of |gLuminous Swamp Moss|n. "
        "It only grows in the damp, murky shallows of the |wSunken Mire|n, east across the Misty River.\n\n"
        "The swamp is treacherous, but if you bring me a cluster of the moss, "
        "I will brew you a concentrated |rGlowing Health Elixir|n and reward you with gold sovereigns! Will you seek it?\""
    )
    options = (
        {"desc": "I accept the task. I will bring you the moss!", "goto": "belladonna_quest_accepted"},
        {"desc": "Swamps sound too dangerous for me right now.", "goto": "belladonna_start_node"}
    )
    return text, options


def belladonna_quest_accepted(caller):
    return (
        "\"Splendid! Cross the North Gate, take the highway north past the Misty River, and search "
        "the Sunken Mire. May fortune favor your footing, traveler!\"",
        ({"desc": "I will return soon.", "goto": None},)
    )


def belladonna_quest_turnin(caller):
    moss_item = None
    for item in caller.contents:
        if "moss" in item.key.lower():
            moss_item = item
            break

    if moss_item:
        moss_item.delete()
        caller.db.belladonna_quest_active = False
        caller.db.completed_belladonna_quest = True

        elixir = create_object(
            Object,
            key="Glowing Health Elixir",
            location=caller,
            aliases=["elixir", "potion", "health potion"],
            tags=["eldoria_world"]
        )
        elixir.db.desc = "A crystal vial filled with shimmering crimson liquid that radiates soothing warmth."
        elixir.db.is_drinkable = True
        elixir.db.drink_type = "elixir"

        gold = create_object(
            Object,
            key="Pouch of Gold Sovereigns",
            location=caller,
            aliases=["gold", "coins", "pouch"],
            tags=["eldoria_world"]
        )
        gold.db.desc = "A heavy leather drawstring pouch clinking with 150 minted gold sovereigns stamped with the wyrm of Eldoria."

        text = (
            "Belladonna gasps with sheer delight as she takes the glowing moss from your hands!\n\n"
            "\"Marvelous! The luminescent quality is pristine! As promised, take this freshly brewed "
            "|rGlowing Health Elixir|n and this pouch of |yGold Sovereigns|n for your brave service.\n\n"
            "You have the gratitude of the Silver Crucible, adventurer!\""
        )
    else:
        text = (
            "Belladonna peers at your pack and shakes her head gently.\n\n"
            "\"You don't seem to have the |gLuminous Swamp Moss|n with you, dear. "
            "Head north through the woods, cross the river, and search the dark marsh water!\""
        )

    options = (
        {"desc": "Thank you, Madam Belladonna!", "goto": "belladonna_start_node"},
        {"desc": "I'll be taking my leave now.", "goto": None}
    )
    return text, options


def belladonna_quest_aftermath(caller):
    text = (
        "\"Thanks to your bravery in the mire, my cauldron bubbles happily! "
        "If you ever need an elixir, you know where to find me.\""
    )
    options = (
        {"desc": "Good to see you well.", "goto": "belladonna_start_node"},
        {"desc": "Farewell.", "goto": None}
    )
    return text, options


def belladonna_farewell(caller):
    return "\"May the stars guide your footsteps through the wild, traveler.\"", None


# =============================================================================
# 3. LORD COMMANDER VALERIUS (Eldoria North Gate)
# =============================================================================

def valerius_start_node(caller):
    has_crown = any("crown" in i.key.lower() for i in caller.contents)
    has_silverware = any("silverware" in i.key.lower() for i in caller.contents)
    has_ledger = any("ledger" in i.key.lower() for i in caller.contents)

    text = (
        "|cLord Commander Valerius|n rests a gauntleted hand on the pommel of his broadsword, "
        "his steely grey eyes appraising you from head to toe.\n\n"
        "\"Halt, citizen. Beyond this gate lies the frontier. State your business.\""
    )

    options = [
        {"desc": "What lies along the road north?", "goto": "valerius_scouting"},
        {"desc": "Are there any bounties or threats to the city I can help eliminate?", "goto": "valerius_bounty_offer"},
    ]

    if has_crown and not caller.db.champion_of_eldoria:
        options.append({
            "desc": "I present the Crown of the Hollow Sovereign! [Claim Royal Bounty]",
            "goto": "valerius_bounty_turnin"
        })

    if has_silverware and not caller.db.recovered_silverware:
        options.append({
            "desc": "I recovered the Royal Silverware from the goblin chief! [Turn in]",
            "goto": "valerius_silverware_turnin"
        })

    if has_ledger and not caller.db.turned_in_ledger:
        options.append({
            "desc": "I found this Smuggler's Cipher Ledger in the harbor warehouse! [Expose Smugglers]",
            "goto": "valerius_ledger_turnin"
        })

    if caller.db.champion_of_eldoria:
        options.append({
            "desc": "Commander, reporting in as Champion of Eldoria.",
            "goto": "valerius_champion"
        })

    options.append({"desc": "Just passing through. Stand easy, Commander.", "goto": "valerius_farewell"})
    return text, tuple(options)


def valerius_scouting(caller):
    text = (
        "Valerius points northward through the iron portcullis:\n\n"
        "\"The King's Highway runs through the Whispering Woods, past the Misty River, all the way to the "
        "craggy northern foothills. In the mountains sits the cursed Hollow Gate—an entrance into the ancient crypts.\n\n"
        "Mind the goblin raiders in the rocks. They have ambushed our patrols twice this season.\""
    )
    options = (
        {"desc": "Understood. Tell me more.", "goto": "valerius_start_node"},
        {"desc": "I will proceed with caution.", "goto": None}
    )
    return text, options


def valerius_bounty_offer(caller):
    text = (
        "Valerius's expression turns grave:\n\n"
        "\"The High Council has posted three critical matters:\n\n"
        "1. |rThe Hollow King|n slumbers in the deepest mountain crypt. Bring me the |wCrown of the Hollow Sovereign|n!\n"
        "2. |gChief Snaggletooth|n and his goblin skulkers raided a royal wagon. We want that stolen silverware back!\n"
        "3. Smuggling cartels are operating along the south docks. Any hard evidence will earn a heavy reward.\""
    )
    options = (
        {"desc": "I will handle these threats for the city!", "goto": "valerius_start_node"},
        {"desc": "Understood. (Step away)", "goto": None}
    )
    return text, options


def valerius_bounty_turnin(caller):
    crown_item = next((i for i in caller.contents if "crown" in i.key.lower()), None)
    if crown_item:
        crown_item.delete()
        caller.db.champion_of_eldoria = True

        crest = create_object(
            Object,
            key="Knight's Crest of Eldoria",
            location=caller,
            aliases=["crest", "medallion", "crest of eldoria"],
            tags=["eldoria_world"]
        )
        crest.db.desc = "A gleaming silver medallion depicting the dragon and tower of Eldoria. Denotes true knighthood."

        royal_gold = create_object(
            Object,
            key="Heavy Sack of Royal Gold",
            location=caller,
            aliases=["gold", "royal gold", "sack"],
            tags=["eldoria_world"]
        )
        royal_gold.db.desc = "A velvet sack containing 500 royal minted gold pieces bearing the seal of High Command."

        text = (
            "Valerius stares at the blackened wrought-iron crown in awe. The guards atop the battlements "
            "snap to crisp attention!\n\n"
            "\"By the gods... you actually breached the crypt and felled the Hollow King!\n\n"
            "In the name of the Crown and City of Eldoria, I confer upon you the |wKnight's Crest of Eldoria|n and "
            "grant you this royal bounty of |y500 Gold Sovereigns|n!\n\n"
            "Hail to the Champion of Eldoria!\""
        )
    else:
        text = "Valerius frowns firmly. \"You do not possess the Crown, traveler.\""

    options = (
        {"desc": "Thank you, Commander!", "goto": "valerius_start_node"},
        {"desc": "Back to duty.", "goto": None}
    )
    return text, options


def valerius_silverware_turnin(caller):
    silver_item = next((i for i in caller.contents if "silverware" in i.key.lower()), None)
    if silver_item:
        silver_item.delete()
        caller.db.recovered_silverware = True

        gold = create_object(
            Object,
            key="Pouch of Gold Sovereigns",
            location=caller,
            aliases=["gold", "coins", "pouch"],
            tags=["eldoria_world"]
        )
        gold.db.desc = "A heavy leather drawstring pouch containing 250 minted gold sovereigns."

        text = (
            "Valerius laughs with relief as he inspects the hallmark on the silver platters.\n\n"
            "\"Outstanding work! The lord mayor was furious about this theft. "
            "Here is your bounty of |y250 Gold Sovereigns|n! You've dealt those goblin vermin a stinging blow.\""
        )
    else:
        text = "You don't have the stolen silverware."

    options = (
        {"desc": "Glad to assist the guard.", "goto": "valerius_start_node"},
        {"desc": "Farewell.", "goto": None}
    )
    return text, options


def valerius_ledger_turnin(caller):
    ledger_item = next((i for i in caller.contents if "ledger" in i.key.lower()), None)
    if ledger_item:
        ledger_item.delete()
        caller.db.turned_in_ledger = True

        badge = create_object(
            Object,
            key="City Guard Badge of Honor",
            location=caller,
            aliases=["badge", "guard badge"],
            tags=["eldoria_world"]
        )
        badge.db.desc = "An enameled brass badge naming you an Honorary Deputy of the Eldoria City Watch."

        gold = create_object(
            Object,
            key="Pouch of Gold Sovereigns",
            location=caller,
            aliases=["gold", "coins", "pouch"],
            tags=["eldoria_world"]
        )
        gold.db.desc = "A pouch of 200 minted gold sovereigns."

        text = (
            "Valerius's eyes widen as he flips through the pages of the cipher ledger!\n\n"
            "\"Good gods... names of harbormasters, payoffs, secret shipments through the cellar! "
            "This is the smoking gun we've needed for months! Take this |wCity Guard Badge of Honor|n and |y200 Gold|n! "
            "We're raiding the docks tonight!\""
        )
    else:
        text = "You do not have the ledger."

    options = (
        {"desc": "Justice is served, Commander.", "goto": "valerius_start_node"},
        {"desc": "Farewell.", "goto": None}
    )
    return text, options


def valerius_champion(caller):
    text = (
        "Valerius salutes you smartly.\n\n"
        "\"Hail, Knight of Eldoria! The northern roads are safer today thanks to your valor. "
        "The city will never forget your service.\""
    )
    options = (
        {"desc": "Honored to serve.", "goto": "valerius_start_node"},
        {"desc": "Carry on, Commander.", "goto": None}
    )
    return text, options


def valerius_farewell(caller):
    return "\"Keep your wits sharp and your steel oiled on the highway.\"", None


# =============================================================================
# 4. GORIM THUNDERHAMMER (Thunderhammer Forge)
# =============================================================================

def gorim_start_node(caller):
    text = (
        "|cGorim Thunderhammer|n strikes a glowing bar of orange steel upon his anvil with a resounding *CLANG*! "
        "He quenches it in a barrel of hissing brine, wipes sweat from his brow, and grins through his bushy red beard.\n\n"
        "\"Aye! Welcome to the forge! Smell that coal smoke? That's the breath of honest labor! What brings ye in?\""
    )
    options = (
        {"desc": "Can you tell me about the weapons forged here?", "goto": "gorim_weapons"},
        {"desc": "Have you heard anything about the locked gate in the mountain crypts?", "goto": "gorim_gate_lore"},
        {"desc": "How is your apprentice Tobin doing?", "goto": "gorim_tobin"},
        {"desc": "Farewell, Gorim.", "goto": "gorim_farewell"}
    )
    return text, options


def gorim_weapons(caller):
    text = (
        "Gorim taps the flat of a newly honed steel broadsword.\n\n"
        "\"High-carbon iron from the northern crags, folded thirty times and quenched in mountain spring water! "
        "A blade like that will cut through goblin shields like butter. Take the sword on the rack if ye need steel at your side!\""
    )
    options = (
        {"desc": "Good craftsmanship. Tell me about something else.", "goto": "gorim_start_node"},
        {"desc": "Thanks, master smith.", "goto": None}
    )
    return text, options


def gorim_gate_lore(caller):
    text = (
        "Gorim's bushy eyebrows shoot up with a hearty laugh:\n\n"
        "\"That locked portcullis in the catacombs? Ha! That lock was forged by my great-uncle Bror! "
        "Unbreakable dwarven tumbler mechanism. You can't bash it down with a siege engine!\n\n"
        "It takes a heavy, notched |wRusty Iron Key|n. Last I heard, a pack of thieving goblin skulkers "
        "stole that key from a patrol and hauled it back to their foul subterranean camp in the crypts. "
        "Find the key in their outpost, and uncle Bror's lock will open smooth as honey!\""
    )
    options = (
        {"desc": "That is invaluable advice, Gorim!", "goto": "gorim_start_node"},
        {"desc": "Time to hunt down some goblins. Farewell!", "goto": None}
    )
    return text, options


def gorim_tobin(caller):
    text = (
        "Gorim sighs and shakes his head with fond exasperation:\n\n"
        "\"Good lad, but clumsy as an ox on ice! He was tinkering with the furnace bellows gearbox "
        "and dropped the main drive cog somewhere out in the plaza! Speak to him if ye can lend him a hand.\""
    )
    options = (
        {"desc": "I'll see if I can help him.", "goto": "gorim_start_node"},
        {"desc": "Farewell.", "goto": None}
    )
    return text, options


def gorim_farewell(caller):
    return "\"Keep your hammer swinging and your hearth fire bright!\"", None


# =============================================================================
# 5. TOBIN THE APPRENTICE (Quest: The Missing Clockwork Cog)
# =============================================================================

def tobin_start_node(caller):
    has_cog = any("cog" in i.key.lower() for i in caller.contents)
    completed = caller.db.completed_tobin_cog

    text = (
        "|cTobin the Apprentice Smith|n is on his knees frantically wiping grease from his hands, "
        "peering under workbenches with panicked eyes.\n\n"
        "\"Oh by the forge... Master Gorim is going to tan my hide! Have you seen a brass gear around?\""
    )

    options = []
    if not completed and not has_cog:
        options.append({
            "desc": "What happened to the gear, Tobin?",
            "goto": "tobin_story"
        })
    elif has_cog and not completed:
        options.append({
            "desc": "I found your Oiled Copper Cog in the plaza fountain! [Hand over Cog]",
            "goto": "tobin_turnin"
        })
    elif completed:
        options.append({
            "desc": "How are the furnace bellows running now?",
            "goto": "tobin_aftermath"
        })

    options.append({"desc": "Good luck finding it, Tobin.", "goto": "tobin_farewell"})
    return text, tuple(options)


def tobin_story(caller):
    caller.db.tobin_quest_active = True
    text = (
        "Tobin groans miserably:\n\n"
        "\"I was washing the grease off the |wOiled Copper Cog|n by the Grand Wyrm Fountain in the plaza, "
        "and it slipped right into the drain basin! The water was too cold and deep for me to fish it out without "
        "a crowd gathering.\n\n"
        "If you can retrieve it from the plaza fountain and bring it back, I'll give you Master Gorim's special whetstone!\""
    )
    options = (
        {"desc": "I'll check the fountain for your cog.", "goto": None},
        {"desc": "Back to work.", "goto": "tobin_start_node"}
    )
    return text, options


def tobin_turnin(caller):
    cog_item = next((i for i in caller.contents if "cog" in i.key.lower()), None)
    if cog_item:
        cog_item.delete()
        caller.db.completed_tobin_cog = True

        whetstone = create_object(
            Object,
            key="Tempered Iron Whetstone",
            location=caller,
            aliases=["whetstone", "stone"],
            tags=["eldoria_world"]
        )
        whetstone.db.desc = "A finely textured dwarven whetstone used to hone blades to razor sharpness."

        text = (
            "Tobin gasps with uncontainable joy and hugs the greasy gear to his chest!\n\n"
            "\"You found it! You saved my apprenticeship! Here, take this |wTempered Iron Whetstone|n—it's forged "
            "from mountain magnetite and keeps blades sharper than dragon teeth! Thank you!\""
        )
    else:
        text = "\"You don't have the cog?\""

    options = (
        {"desc": "Glad to help, Tobin!", "goto": None},
    )
    return text, options


def tobin_aftermath(caller):
    return "\"The bellows are pumping like a dream! Master Gorim hasn't suspected a thing!\"", None


def tobin_farewell(caller):
    return "\"Watch your step around the hot coals!\"", None


# =============================================================================
# 6. SISTER MEREDITH & PIP (Quest: The Stolen Sun Chalice)
# =============================================================================

def meredith_start_node(caller):
    has_chalice = any("chalice" in i.key.lower() for i in caller.contents)
    has_shard = any("soul-shard" in i.key.lower() or "shard" in i.key.lower() for i in caller.contents)
    completed_chalice = caller.db.completed_chalice_quest

    text = (
        "|cSister Meredith|n stands before the solar emblem altar, her head bowed in tranquil meditation. "
        "As you draw near, she looks up with serene, compassionate eyes.\n\n"
        "\"Peace be with you, child of the dawn. What brings your spirit to the cathedral?\""
    )

    options = []
    if not completed_chalice and not has_chalice:
        options.append({
            "desc": "You seem troubled, Sister. Is everything all right?",
            "goto": "meredith_chalice_story"
        })
    elif has_chalice and not completed_chalice:
        options.append({
            "desc": "I have recovered the Gilded Sun Chalice! [Return Chalice]",
            "goto": "meredith_chalice_turnin"
        })

    if has_shard and not caller.db.cleansed_phylactery:
        options.append({
            "desc": "I bring the Black Soul-Shard of the Hollow King to be cleansed! [Perform Rite]",
            "goto": "meredith_purify_shard"
        })

    options.append({"desc": "May the light watch over you, Sister.", "goto": "meredith_farewell"})
    return text, tuple(options)


def meredith_chalice_story(caller):
    caller.db.chalice_quest_active = True
    text = (
        "Sister Meredith sighs softly:\n\n"
        "\"Alas, our sacred |wGilded Sun Chalice|n was taken from the altar yesterday by a desperate child "
        "who fled toward the Sunken Bazaar. I hold no malice toward him—times are hard for street urchins—but "
        "the chalice holds centuries of consecrated solar blessing.\n\n"
        "Please, find the young boy—Pip—in the bazaar. Persuade him gently to return the chalice, perhaps with food, "
        "and bring it back to the dawn altar.\""
    )
    options = (
        {"desc": "I will find Pip and recover the chalice peacefully.", "goto": None},
        {"desc": "I understand.", "goto": "meredith_start_node"}
    )
    return text, options


def meredith_chalice_turnin(caller):
    chalice = next((i for i in caller.contents if "chalice" in i.key.lower()), None)
    if chalice:
        chalice.delete()
        caller.db.completed_chalice_quest = True

        rosary = create_object(
            Object,
            key="Sister Meredith's Rosary of Dawn",
            location=caller,
            aliases=["rosary", "beads", "rosary of dawn"],
            tags=["eldoria_world"]
        )
        rosary.db.desc = "A strand of amber prayer beads warmed by solar radiance. Protects the bearer against dark spirits."

        text = (
            "Sister Meredith receives the chalice with reverent gratitude and sets it upon the gilded altar cloths.\n\n"
            "\"Blessed be the light! You brought it back with compassion and honor. "
            "Please, wear this |wRosary of Dawn|n. May its amber glow ward off the gloom of dark dungeons and "
            "guide your heart.\""
        )
    else:
        text = "\"You do not carry the chalice, child.\""

    options = (
        {"desc": "Thank you, Sister Meredith.", "goto": None}
    )
    return text, options


def meredith_purify_shard(caller):
    shard = next((i for i in caller.contents if "shard" in i.key.lower()), None)
    if shard:
        shard.delete()
        caller.db.cleansed_phylactery = True

        cloak = create_object(
            Object,
            key="Radiant Cloak of the Dawn Sentinel",
            location=caller,
            aliases=["cloak", "radiant cloak"],
            tags=["eldoria_world"]
        )
        cloak.db.desc = "A magnificent white mantle embroidered with golden sunbursts. It hums with divine serenity."

        text = (
            "Sister Meredith raises her hands as you set the jagged obsidian Black Soul-Shard upon the altar. "
            "She begins an ancient hymn in the sacred tongue.\n\n"
            "A pillar of pure golden sunlight erupts through the cathedral dome, striking the shard! "
            "With a deafening crack, the shadowy crystal shatters into pure sparkling stardust! A joyful chime "
            "echoes through the cathedral as the lingering curse upon the land is permanently lifted!\n\n"
            "Sister Meredith presents you with the |wRadiant Cloak of the Dawn Sentinel|n!\n\n"
            "\"You are the true Bane of the Hollow Sovereign! Eldoria owes you an eternal debt.\""
        )
    else:
        text = "You do not have the soul-shard."

    options = (
        {"desc": "The light has prevailed!", "goto": None}
    )
    return text, options


def meredith_farewell(caller):
    return "\"Walk in the radiance of the morning sun, traveler.\"", None


def pip_start_node(caller):
    has_bun = any("bun" in i.key.lower() or "pastry" in i.key.lower() for i in caller.contents)
    given_chalice = caller.db.pip_gave_chalice

    text = (
        "|cPip the Street Urchin|n darts between the silk market stalls like a rabbit, clutching "
        "a bulging burlap sack behind his back. He eyes you warily.\n\n"
        "\"I didn't do nothin'! You ain't a guardsman, are ya? Back off!\""
    )

    options = []
    if not given_chalice:
        if has_bun:
            options.append({
                "desc": "Here, Pip. I bought this fresh Sweet Honey Bun for you. [Offer Pastry]",
                "goto": "pip_offer_bun"
            })
        options.append({
            "desc": "Sister Meredith isn't angry at you, Pip. She just wants the chalice back.",
            "goto": "pip_persuade"
        })
    else:
        options.append({
            "desc": "How are you doing today, Pip?",
            "goto": "pip_friendly"
        })

    options.append({"desc": "Keep out of trouble, kid.", "goto": None})
    return text, tuple(options)


def pip_offer_bun(caller):
    bun = next((i for i in caller.contents if "bun" in i.key.lower() or "pastry" in i.key.lower()), None)
    if bun:
        bun.delete()
    caller.db.pip_gave_chalice = True

    chalice = create_object(
        Object,
        key="Gilded Sun Chalice",
        location=caller,
        aliases=["chalice", "sun chalice", "golden chalice"],
        tags=["eldoria_world"]
    )
    chalice.db.desc = "A sacred chalice forged of pure gold and studded with radiant yellow citrine stones."

    text = (
        "Pip's eyes go wide at the sight of the warm, sugar-dusted pastry. His stomach growls audibly.\n\n"
        "He hungrily grabs the bun and takes a massive bite, a huge grin spreading across his dusty cheeks.\n\n"
        "\"Mmmm! Honey and cinnamon! Look... I didn't wanna steal nothin' bad, I was just starving. "
        "Here's the shiny cup from the church. Tell Sister Meredith I'm sorry!\""
    )
    options = (
        {"desc": "Eat up, Pip. I will deliver it to her safely.", "goto": None}
    )
    return text, options


def pip_persuade(caller):
    caller.db.pip_gave_chalice = True

    chalice = create_object(
        Object,
        key="Gilded Sun Chalice",
        location=caller,
        aliases=["chalice", "sun chalice", "golden chalice"],
        tags=["eldoria_world"]
    )
    chalice.db.desc = "A sacred chalice forged of pure gold and studded with radiant yellow citrine stones."

    text = (
        "Pip lowers his guard, blinking back tears of relief.\n\n"
        "\"She... she really ain't gonna send the guards after me? Honest?\n\n"
        "He reaches into his burlap sack and pulls out the |wGilded Sun Chalice|n, handing it to you with both hands.\n\n"
        "\"Take it back. I don't want no curses on my head!\""
    )
    options = (
        {"desc": "You made the right choice, Pip.", "goto": None}
    )
    return text, options


def pip_friendly(caller):
    return "\"Thanks to you, I've got bread in my belly! The market guards haven't chased me all morning!\"", None


# =============================================================================
# 7. SILAS "GULL" VANE (Quest: The Smuggler's Cipher)
# =============================================================================

def silas_start_node(caller):
    has_ledger = any("ledger" in i.key.lower() for i in caller.contents)

    text = (
        "|cSilas 'Gull' Vane|n leans nervously against a wooden mooring post on the docks, "
        "constantly looking over his shoulder toward the Old Salt Warehouse.\n\n"
        "\"Hey... keep it down, mate! The fog has ears around these docks. What do you want?\""
    )

    options = [
        {"desc": "What's going on with that warehouse behind you?", "goto": "silas_rumor"},
    ]

    if has_ledger:
        options.append({
            "desc": "Is this Wax-Sealed Cipher Ledger yours, Silas? [Confront Silas]",
            "goto": "silas_confront"
        })

    options.append({"desc": "Move along, Silas.", "goto": None})
    return text, tuple(options)


def silas_rumor(caller):
    text = (
        "Silas drops his voice to an urgent whisper:\n\n"
        "\"Between you and me? Strange crates come off the smuggler luggers at midnight. "
        "They move 'em into the warehouse, and then *poof*—they vanish! I swear there's a false wall or hatch "
        "in there leading under the city. If the City Watch finds the ledger inside, we're all done for!\""
    )
    options = (
        {"desc": "Interesting... (Search the warehouse)", "goto": None}
    )
    return text, options


def silas_confront(caller):
    text = (
        "Silas turns white as a sheet, sweating profusely.\n\n"
        "\"Shhh! Put that away! If Commander Valerius sees that, I'm heading to the dungeon for life!\n\n"
        "Look, give that ledger to Valerius at the North Gate if you want justice... or keep it quiet. "
        "Just don't tell 'em you got it from me!\""
    )
    options = (
        {"desc": "I will deliver this to Commander Valerius.", "goto": None}
    )
    return text, options


# =============================================================================
# 8. SCOUT HEATHER (Quest: The Broken Watchtower Beacon)
# =============================================================================

def heather_start_node(caller):
    completed = caller.db.lit_beacon

    text = (
        "|cScout Heather|n leans against an ancient pine at the edge of the woods, "
        "clutching a bandaged arm. Her quiver of arrows is strapped across her leather tunic.\n\n"
        "\"Greetings, traveler. Keep your eyes on the ridge. The northern watchtower has gone dark.\""
    )

    options = []
    if not completed:
        options.append({
            "desc": "Why is the watchtower dark, Scout Heather?",
            "goto": "heather_quest_offer"
        })
        options.append({
            "desc": "I have ascended the watchtower and lit the beacon fire! [Report Success]",
            "goto": "heather_turnin"
        })
    else:
        options.append({
            "desc": "The beacon burns brightly across the valley!",
            "goto": "heather_aftermath"
        })

    options.append({"desc": "Stay safe, ranger.", "goto": None})
    return text, tuple(options)


def heather_quest_offer(caller):
    caller.db.heather_quest_active = True
    text = (
        "Heather grimaces in pain as she adjusts her bow:\n\n"
        "\"Goblin scouts ambushed me on the ridge and extinguished the signal pyre atop the "
        "|wRuined Hilltop Watchtower|n. Without that beacon, the garrison in Eldoria cannot see enemy troop movements.\n\n"
        "Take the highway north past the river, climb up the craggy foothills to the watchtower, and "
        "light the signal pyre! There should be dry kindling in the deep woods if you need tinder.\""
    )
    options = (
        {"desc": "I will climb the watchtower and relight the beacon!", "goto": None}
    )
    return text, options


def heather_turnin(caller):
    beacon_lit = caller.db.pyre_is_lit
    if beacon_lit:
        caller.db.lit_beacon = True

        quiver = create_object(
            Object,
            key="Ranger's Scout Quiver",
            location=caller,
            aliases=["quiver", "scout quiver"],
            tags=["eldoria_world"]
        )
        quiver.db.desc = "A supple elven leather quiver trimmed with falcon feathers, lightweight and weather-sealed."

        gold = create_object(
            Object,
            key="Pouch of Gold Sovereigns",
            location=caller,
            aliases=["gold", "coins", "pouch"],
            tags=["eldoria_world"]
        )
        gold.db.desc = "A pouch containing 100 gold sovereigns."

        text = (
            "Heather looks up toward the distant peaks, where a soaring plume of bright white smoke "
            "now climbs into the clouds!\n\n"
            "\"You did it! The beacon burns once more! Eldoria's scouts can see the pass!\n\n"
            "Take this |wRanger's Scout Quiver|n and this pouch of |y100 Gold Sovereigns|n as our heartfelt reward. "
            "You are a true friend of the wild scouts!\""
        )
    else:
        text = (
            "Heather looks to the peaks and shakes her head.\n\n"
            "\"The hilltop pyre is still dark, traveler. Climb up from the craggy foothills and light the beacon!\""
        )

    options = (
        {"desc": "Understood, Heather!", "goto": None}
    )
    return text, options


def heather_aftermath(caller):
    return "\"Thanks to that beacon, our scouting patrols are safe from ambushes! Fair winds to you!\"", None


# =============================================================================
# 9. THE WHISPERING SENTINEL (Quest: Rite of the Ancient Stones)
# =============================================================================

def sentinel_start_node(caller):
    has_pearl = any("pearl" in i.key.lower() for i in caller.contents)
    has_blossom = any("blossom" in i.key.lower() for i in caller.contents)
    has_dust = any("dust" in i.key.lower() for i in caller.contents)
    completed = caller.db.completed_stone_rite

    text = (
        "|cThe Whispering Sentinel|n, an ancient moss-covered stone face carved into the colossal monolith, "
        "opens deep hollow eyes as you approach. Emerald light glows within the stone runes.\n\n"
        "A voice like grinding granite echoes inside your mind:\n\n"
        "\"MORTAL SOUL... SEEKER OF THE FOREST... DO YOU BRING THE THREE SEALS OF THE CYCLE?\""
    )

    options = []
    if not completed:
        options.append({
            "desc": "What are the three seals of the cycle?",
            "goto": "sentinel_riddle"
        })
        if has_pearl and has_blossom and has_dust:
            options.append({
                "desc": "I offer the River Pearl, Sunburst Blossom, and Grave Dust! [Complete Rite]",
                "goto": "sentinel_turnin"
            })
    else:
        options.append({
            "desc": "The grove is at peace, Sentinel.",
            "goto": "sentinel_peace"
        })

    options.append({"desc": "Step away with reverent bow.", "goto": None})
    return text, tuple(options)


def sentinel_riddle(caller):
    text = (
        "The stone face rumbles solemnly:\n\n"
        "\"THE ANCIENTS REQUIRED THREE ELEMENTS TO BLESS THIS LAND:\n"
        "- THE TEARS OF THE RUSHING STREAM: A |wRiver Pearl|n from the Misty River Crossing.\n"
        "- THE FIRE OF THE SUMMER SUN: A |wSunburst Blossom|n blooming in the Deep Woods.\n"
        "- THE MEMORY OF THE FALLEN: |wGrave Dust|n from the threshold of the Hollow Gate.\n\n"
        "BRING THEM TOGETHER BEFORE THIS ALTAR, AND RECEIVE NATURE'S HEART.\""
    )
    options = (
        {"desc": "I shall gather the three seals.", "goto": None}
    )
    return text, options


def sentinel_turnin(caller):
    pearl = next((i for i in caller.contents if "pearl" in i.key.lower()), None)
    blossom = next((i for i in caller.contents if "blossom" in i.key.lower()), None)
    dust = next((i for i in caller.contents if "dust" in i.key.lower()), None)

    if pearl and blossom and dust:
        pearl.delete()
        blossom.delete()
        dust.delete()
        caller.db.completed_stone_rite = True

        amulet = create_object(
            Object,
            key="Amulet of the Verdant Oak",
            location=caller,
            aliases=["amulet", "oak amulet", "verdant amulet"],
            tags=["eldoria_world"]
        )
        amulet.db.desc = "A talisman carved of petrified oak that pulses with a soothing emerald vitality."

        text = (
            "You place the pearl, blossom, and dust upon the central mossy altar.\n\n"
            "Vines of ivy surge across the stone, erupting into fragrant, luminous orchids! "
            "A warm green radiance envelops you, lifting all fatigue from your limbs.\n\n"
            "\"THE BALANCE IS RESTORED. ACCEPT THIS |wAmulet of the Verdant Oak|n. "
            "MAY THE ANCIENT ROOTS SHELTER THEE, GUARDIAN.\""
        )
    else:
        text = "\"You do not have all three seals.\""

    options = (
        {"desc": "Reverently accept the blessing.", "goto": None}
    )
    return text, options


def sentinel_peace(caller):
    return "\"THE GROVE BLOSSOMS. WALK WITH OUR BLESSING, CHILD OF NATURE.\"", None


# =============================================================================
# 10. MIRELLA THE BOG WITCH (Quest: The Lost Familiar)
# =============================================================================

def mirella_start_node(caller):
    has_toad = any("toad" in i.key.lower() for i in caller.contents)
    completed = caller.db.returned_toad

    text = (
        "|cMirella the Bog Witch|n stirs a foul-smelling cauldron of black bubbling broth, "
        "cackling softly to herself. Her yellow eyes fix upon you with intense amusement.\n\n"
        "\"Hee-hee! What wanderer squelches through my bog? Come to be turned into a newt?\""
    )

    options = []
    if not completed and not has_toad:
        options.append({
            "desc": "Are you in need of any assistance, Mirella?",
            "goto": "mirella_toad_quest"
        })
    elif has_toad and not completed:
        options.append({
            "desc": "I found Barnaby-Toad swimming in the marsh! [Hand over Toad]",
            "goto": "mirella_toad_turnin"
        })
    elif completed:
        options.append({
            "desc": "How is Barnaby-Toad doing?",
            "goto": "mirella_toad_aftermath"
        })

    options.append({"desc": "Back away slowly from the cauldron.", "goto": None})
    return text, tuple(options)


def mirella_toad_quest(caller):
    caller.db.mirella_quest_active = True
    text = (
        "Mirella's crooked smile turns into an angry scowl:\n\n"
        "\"My beloved three-eyed familiar, |gBarnaby-Toad|n, took fright and hopped into the murky swamp! "
        "He's out there somewhere among the reeds in the Sunken Mire, croaking his poor lungs out!\n\n"
        "Take this jar of glowing fire-beetles from my shelf—he can't resist 'em! Scoop him up and "
        "bring him back to my hut, and I'll brew you a jar of my legendary |wBog Salve|n!\""
    )
    options = (
        {"desc": "I will find your three-eyed toad, Mirella.", "goto": None}
    )
    return text, options


def mirella_toad_turnin(caller):
    toad = next((i for i in caller.contents if "toad" in i.key.lower()), None)
    if toad:
        toad.delete()
        caller.db.returned_toad = True

        salve = create_object(
            Object,
            key="Jar of Mystical Bog Salve",
            location=caller,
            aliases=["salve", "bog salve", "jar"],
            tags=["eldoria_world"]
        )
        salve.db.desc = "A clay jar containing glowing green swamp salve that cures poison, burns, and rot."
        salve.db.is_drinkable = True
        salve.db.drink_type = "elixir"

        text = (
            "Mirella shrieks with cackling glee as she plucks the three-eyed amphibian and cradles it "
            "against her ragged shawl!\n\n"
            "\"My precious slimy prince! You found him! Hee-hee!\n\n"
            "Here, take this |wJar of Mystical Bog Salve|n! Rub it on your cuts or drink it down—it'll cure "
            "any snake bite, goblin rot, or crypt chill you ever suffer! Now off with ye!\""
        )
    else:
        text = "\"You don't have my toad!\""

    options = (
        {"desc": "Take care of your toad, Mirella!", "goto": None}
    )
    return text, options


def mirella_toad_aftermath(caller):
    return "\"Barnaby-Toad is fat and happy, feasting on swamp flies! Hee-hee!\"", None


# =============================================================================
# 11. OLD MAN CORVUS (Quest: The Will-O'-Wisp Lantern)
# =============================================================================

def corvus_start_node(caller):
    has_wisp_lantern = any("blazing" in i.key.lower() and "lantern" in i.key.lower() for i in caller.contents)
    has_empty_lantern = any("ghost-iron" in i.key.lower() for i in caller.contents)

    text = (
        "|cOld Man Corvus|n sits hunched on an overturned peat barrel at the edge of the swamp, "
        "smoking a clay pipe filled with pungent marsh weed.\n\n"
        "\"Misty night, traveler. The bogs swallow those who travel without spirit fire.\""
    )

    options = []
    if not has_wisp_lantern and not has_empty_lantern:
        options.append({
            "desc": "What is spirit fire, old man?",
            "goto": "corvus_wisp_story"
        })
    elif has_empty_lantern and not has_wisp_lantern:
        options.append({
            "desc": "How do I catch the will-o'-the-wisp in this lantern?",
            "goto": "corvus_wisp_instructions"
        })
    elif has_wisp_lantern:
        options.append({
            "desc": "I have trapped the spirit fire in the lantern!",
            "goto": "corvus_wisp_success"
        })

    options.append({"desc": "Safe journey through the fog.", "goto": None})
    return text, tuple(options)


def corvus_wisp_story(caller):
    lantern = create_object(
        Object,
        key="Empty Ghost-Iron Lantern",
        location=caller,
        aliases=["lantern", "ghost lantern"],
        tags=["eldoria_world"]
    )
    lantern.db.desc = "A cold, unlit cage of filigreed spirit iron designed to hold captive will-o'-the-wisps."

    text = (
        "Corvus exhales a ring of pale blue smoke and hands you a dark metal lantern:\n\n"
        "\"The will-o'-the-wisps dance across the Sunken Mire. Catch one in this |wEmpty Ghost-Iron Lantern|n, "
        "and you'll possess a beacon of spirit fire that never dims and reveals hidden doors in the dark.\n\n"
        "Take the lantern into the mire and scoop up a dancing wisp!\""
    )
    options = (
        {"desc": "I will capture a wisp.", "goto": None}
    )
    return text, options


def corvus_wisp_instructions(caller):
    text = (
        "\"Wander into the center of the mire, find the dancing blue wisp, and capture it! "
        "The ghost iron will trap the spirit without harming it.\""
    )
    options = (
        {"desc": "Understood.", "goto": None}
    )
    return text, options


def corvus_wisp_success(caller):
    return "\"Ah! Look at that sapphire glow! The darkness will never blind you now, traveler.\"", None


# =============================================================================
# 12. LADY ELSPETH (Quest: Rest for the Weeping Maiden)
# =============================================================================

def elspeth_start_node(caller):
    has_locket = any("locket" in i.key.lower() for i in caller.contents)
    completed = caller.db.completed_elspeth_quest

    text = (
        "|cLady Elspeth|n, a translucent ghostly apparition in shredded burial silks, "
        "floats above the black mineral pool in the Sunken Ossuary. She weeps silently into spectral hands.\n\n"
        "\"Lost... all lost... taken by the grave thieves into the dark dust...\""
    )

    options = []
    if not completed and not has_locket:
        options.append({
            "desc": "Why do you weep, spirit?",
            "goto": "elspeth_story"
        })
    elif has_locket and not completed:
        options.append({
            "desc": "I found your Silver Filigree Locket in the antechamber! [Return Locket]",
            "goto": "elspeth_turnin"
        })
    elif completed:
        options.append({
            "desc": "Rest peacefully, Lady Elspeth.",
            "goto": "elspeth_peace"
        })

    options.append({"desc": "Step quietly away from the apparition.", "goto": None})
    return text, tuple(options)


def elspeth_story(caller):
    caller.db.elspeth_quest_active = True
    text = (
        "The specter lifts her sorrowful gaze:\n\n"
        "\"A foul robber desecrated my tomb centuries ago and stole my beloved |wSilver Filigree Locket|n—the "
        "only keepsake of my fallen knight. He fled toward the Dusty Antechamber before the dungeon traps took him.\n\n"
        "Find my locket among the overturned sarcophagi, and bring peace to my wandering soul...\""
    )
    options = (
        {"desc": "I will search the antechamber for your locket.", "goto": None}
    )
    return text, options


def elspeth_turnin(caller):
    locket = next((i for i in caller.contents if "locket" in i.key.lower()), None)
    if locket:
        locket.delete()
        caller.db.completed_elspeth_quest = True

        ring = create_object(
            Object,
            key="Elspeth's Sorrowful Band",
            location=caller,
            aliases=["ring", "band", "sorrowful band"],
            tags=["eldoria_world"]
        )
        ring.db.desc = "A chilling silver ring that glimmers with starlight, granting protection against dark curses."

        text = (
            "Lady Elspeth reaches out trembling spectral hands. As her ethereal fingers touch the locket, "
            "her ghostly tears turn into sparkling diamonds of pure light!\n\n"
            "A serene smile graces her face as her spirit begins dissolving into shimmering silver mist.\n\n"
            "\"Peace... at long last... Take my blessing, gentle traveler: |wElspeth's Sorrowful Band|n. "
            "May it guard your soul when you face the Hollow King...\"\n\n"
            "With a final whisper of gratitude, she vanishes into the peaceful dark."
        )
    else:
        text = "\"You do not have my locket...\""

    options = (
        {"desc": "Farewell, Lady Elspeth.", "goto": None}
    )
    return text, options


def elspeth_peace(caller):
    return "\"A peaceful warmth lingers over the ossuary waters.\"", None


# =============================================================================
# 13. CHIEF SNAGGLETOOTH (Quest: The Goblin Stew Pot)
# =============================================================================

def snaggletooth_start_node(caller):
    text = (
        "|cChief Snaggletooth|n, a squat, bloated goblin wearing a dented copper kettle as a helmet, "
        "brandishes a blackened roasting spit menacingly!\n\n"
        "\"YAAARGH! Who let long-legs into Snaggletooth's throne room?! "
        "We boil you in stew pot with mushrooms!\""
    )
    options = (
        {"desc": "Give up the stolen silverware and the rusty key, goblin!", "goto": "snaggletooth_threat"},
        {"desc": "I brought shiny trinkets to trade! (Bluff)", "goto": "snaggletooth_bluff"},
        {"desc": "Back off, runt! (Brandish weapon)", "goto": "snaggletooth_cower"},
    )
    return text, options


def snaggletooth_threat(caller):
    text = (
        "Snaggletooth's kettle helmet slips over his eyes with a metallic *CLANG*! "
        "He pushes it back up furiously.\n\n"
        "\"Never! Shiny knives and forks belong to Snaggletooth! We stole 'em fair and square from "
        "stupid shiny guards! You want 'em? Search the bone pile! We dare you!\""
    )
    options = (
        {"desc": "Take the loot from the hoard.", "goto": None}
    )
    return text, options


def snaggletooth_bluff(caller):
    text = (
        "Snaggletooth's eyes greedily dart around:\n\n"
        "\"Shiny trinkets?! Ooooh! Leave shiny things by campfire and go away before big Chief eats you!\""
    )
    options = (
        {"desc": "Step back.", "goto": None}
    )
    return text, options


def snaggletooth_cower(caller):
    text = (
        "Seeing your hardened battle stance, Snaggletooth screeches and drops his roasting spit, "
        "diving behind a stack of rotten crates!\n\n"
        "\"Eeeeee! Don't poke Chief! Take whatever you want from the camp pile, just don't poke me!\""
    )
    options = (
        {"desc": "Plunder the goblin hoard.", "goto": None}
    )
    return text, options


# =============================================================================
# 14. BROTHER JONATHAN (Quest: The Hollow King's Phylactery)
# =============================================================================

def jonathan_start_node(caller):
    has_mallet = any("mallet" in i.key.lower() for i in caller.contents)
    cleansed = caller.db.cleansed_phylactery

    text = (
        "|cBrother Jonathan|n, a scholarly monk with spectacles resting upon his nose, "
        "poring over dusty grimoires at a study table in the Arcane Library.\n\n"
        "\"Greetings, adventurer. I study the dark curses that bind restless souls to this world.\""
    )

    options = []
    if not has_mallet and not cleansed:
        options.append({
            "desc": "How can the Hollow King be truly destroyed?",
            "goto": "jonathan_phylactery_lore"
        })
    elif has_mallet and not cleansed:
        options.append({
            "desc": "What do I do once I obtain the Hollow King's Soul-Shard?",
            "goto": "jonathan_instructions"
        })
    elif cleansed:
        options.append({
            "desc": "The phylactery was shattered at the cathedral altar!",
            "goto": "jonathan_success"
        })

    options.append({"desc": "Continue your studies, Brother.", "goto": None})
    return text, tuple(options)


def jonathan_phylactery_lore(caller):
    mallet = create_object(
        Object,
        key="Consecrated Iron Mallet",
        location=caller,
        aliases=["mallet", "consecrated mallet", "hammer"],
        tags=["eldoria_world"]
    )
    mallet.db.desc = "A heavy ritual hammer inscribed with divine runes of dawn, capable of shattering dark soul-shards."

    text = (
        "Brother Jonathan speaks in a hushed, urgent tone:\n\n"
        "\"The Hollow King cannot truly die by steel alone. In his throne room lies his dark |wBlack Soul-Shard|n—his phylactery!\n\n"
        "Take this |wConsecrated Iron Mallet|n. Slay the king, claim his soul-shard, and bring it to the "
        "|wCathedral of the Radiant Dawn|n! Place it upon the golden altar and let Sister Meredith consecrate the ritual.\n\n"
        "Only then will Eldoria truly be free!\""
    )
    options = (
        {"desc": "I accept the consecrated mallet.", "goto": None}
    )
    return text, options


def jonathan_instructions(caller):
    return "\"Bring the soul-shard to the Cathedral altar in town. Sister Meredith knows the sacred rites!\"", None


def jonathan_success(caller):
    return "\"You have cleansed the land of an ancient nightmare, champion! History will remember your name!\"", None


# =============================================================================
# 15. FINCH THE FENCE (The Black Rat Hideout - Sewers)
# =============================================================================

def finch_start_node(caller):
    has_signet = any("signet" in i.key.lower() for i in caller.contents)
    completed = caller.db.completed_finch_job

    text = (
        "|cFinch the Fence|n sits atop a stack of smuggled tea crates, flipping a silver coin through his knuckles.\n\n"
        "\"Step lightly, shadow-walker. Welcome to the Black Rat. Looking for coin, or trying to stay out of the daylight?\""
    )
    options = []
    if not completed and not has_signet:
        options.append({
            "desc": "Are there any profitable jobs for a discrete rogue?",
            "goto": "finch_job_offer"
        })
    elif has_signet and not completed:
        options.append({
            "desc": "I planted the Gilded Noble Signet in the tavern room! [Collect Bounty]",
            "goto": "finch_job_turnin"
        })
    elif completed:
        options.append({
            "desc": "Any new whisperings from the street?",
            "goto": "finch_aftermath"
        })

    options.append({"desc": "Keep your head down, Finch.", "goto": None})
    return text, tuple(options)


def finch_job_offer(caller):
    caller.db.finch_quest_active = True
    signet = create_object(
        Object,
        key="Gilded Noble Signet",
        location=caller,
        aliases=["signet", "ring", "noble signet"],
        tags=["eldoria_world"]
    )
    signet.db.desc = "A heavy gold signet ring engraved with a falcon and magistrate scales. Stolen property!"

    text = (
        "Finch leans in with a toothy, gold-flecked grin:\n\n"
        "\"A corrupt magistrate has been stiffing our guild on protection coin. "
        "Take this |wGilded Noble Signet|n up into the tavern lodgings. Plant it in a dresser, "
        "and our informants will alert the city watch. That magistrate will be out of office by dusk!\n\n"
        "Do the drop, come back, and you'll earn a master set of |wFinch's Lockpicks|n!\""
    )
    options = (
        {"desc": "Consider it done, Finch.", "goto": None}
    )
    return text, options


def finch_job_turnin(caller):
    signet = next((i for i in caller.contents if "signet" in i.key.lower()), None)
    if signet:
        signet.delete()
    caller.db.completed_finch_job = True

    lockpicks = create_object(
        Object,
        key="Finch's Master Lockpick Set",
        location=caller,
        aliases=["lockpicks", "picks", "pick set"],
        tags=["eldoria_world"]
    )
    lockpicks.db.desc = "A sleek leather pouch containing oiled spring-steel tension bars and diamond picks."

    gold = create_object(
        Object,
        key="Pouch of Gold Sovereigns",
        location=caller,
        aliases=["gold", "coins", "pouch"],
        tags=["eldoria_world"]
    )
    gold.db.desc = "A purse containing 150 gold sovereigns."

    text = (
        "Finch cackles with pure delight:\n\n"
        "\"The magistrate was hauled off in irons an hour ago! Beautiful work!\n\n"
        "Here are your |wFinch's Master Lockpicks|n and |y150 Gold|n! You've got friends in the sewers, mate.\""
    )
    options = (
        {"desc": "Pleasure doing business.", "goto": None}
    )
    return text, options


def finch_aftermath(caller):
    return "\"The City Watch is scratching their heads while we count our coin. Good times!\"", None


# =============================================================================
# 16. GRIBBLE THE RAT-CATCHER (Sewer Sluice Gate)
# =============================================================================

def gribble_start_node(caller):
    completed = caller.db.defeated_rat_patriarch

    text = (
        "|cGribble the Rat-Catcher|n rubs the ears of his scruffy terrier Sniffer. "
        "His patchwork coat of rat pelts rustles as he turns toward you.\n\n"
        "\"Mind your boots, traveler! The sludge down here bites back!\""
    )
    options = []
    if not completed:
        options.append({
            "desc": "What kind of vermin are infesting these tunnels?",
            "goto": "gribble_quest"
        })
        options.append({
            "desc": "I have cleared out the Sewer Patriarch in the warren! [Report Kill]",
            "goto": "gribble_turnin"
        })
    else:
        options.append({
            "desc": "Sniffer seems much happier now.",
            "goto": "gribble_aftermath"
        })

    options.append({"desc": "Watch your step, Gribble.", "goto": None})
    return text, tuple(options)


def gribble_quest(caller):
    musk = create_object(
        Object,
        key="Scent-Masking Musk Flask",
        location=caller,
        aliases=["musk", "flask", "scent-masking musk"],
        tags=["eldoria_world"]
    )
    musk.db.desc = "A pungent earthen flask of bitter marsh-herb musk that conceals human scent from vermin."

    text = (
        "Gribble spits into the sludge channel:\n\n"
        "\"The |rSewer Patriarch|n—a giant albino brute the size of a warhound—has taken over the western warren! "
        "Sniffer won't even go near the canal!\n\n"
        "Take this |wScent-Masking Musk Flask|n to keep the smaller rats from swarming you. "
        "Venture into the warren, slay the Patriarch, and bring me peace in the pipes!\""
    )
    options = (
        {"desc": "I will handle the beast, Gribble.", "goto": None}
    )
    return text, options


def gribble_turnin(caller):
    caller.db.defeated_rat_patriarch = True

    cloak = create_object(
        Object,
        key="Gribble's Shadow-Rat Cloak",
        location=caller,
        aliases=["cloak", "rat cloak"],
        tags=["eldoria_world"]
    )
    cloak.db.desc = "A waterproof hide cloak treated with subterranean moss, providing stealth in shadowy corridors."

    gold = create_object(
        Object,
        key="Pouch of Gold Sovereigns",
        location=caller,
        aliases=["gold", "coins", "pouch"],
        tags=["eldoria_world"]
    )
    gold.db.desc = "A pouch of 120 gold sovereigns."

    text = (
        "Gribble lets out a joyous whoop that echoes down the brick tunnel! Sniffer barks excitedly!\n\n"
        "\"By the crown, you slew the Patriarch! The pipes are safe for honest rat-catchers once more!\n\n"
        "Take my prized |wShadow-Rat Cloak|n and this pouch of |y120 Gold|n! You've earned it, sewer hero!\""
    )
    options = (
        {"desc": "Glad to clear the pipes, Gribble.", "goto": None}
    )
    return text, options


def gribble_aftermath(caller):
    return "\"Sniffer and I are catching ordinary river mice again. Much easier on the knees!\"", None


# =============================================================================
# 17. CAPTAIN "ONE-EYE" MORGAN & LORELEI (Smuggler's Bay & Siren Caves)
# =============================================================================

def morgan_start_node(caller):
    has_cutlass = any("cutlass" in i.key.lower() for i in caller.contents)

    text = (
        "|cCaptain 'One-Eye' Morgan|n adjusts his silver hook, gazing out across the storm-lashed breakers "
        "toward the jagged reef where the *Siren's Call* lies wrecked.\n\n"
        "\"Ahoy, landlubber. The sea gives, and the sea takes. Mostly takes around these rocks.\""
    )
    options = [
        {"desc": "Tell me about the shipwreck out on the reef.", "goto": "morgan_wreck_lore"},
        {"desc": "How can one explore the sea cavern without succumbing to the sirens?", "goto": "morgan_siren_tips"},
    ]
    options.append({"desc": "Fair winds, Captain.", "goto": None})
    return text, tuple(options)


def morgan_wreck_lore(caller):
    text = (
        "Morgan points with his hook toward the shattered timber ribs jutting from the foaming reef:\n\n"
        "\"That was the *Siren's Call*—richest merchant brig to sail the southern coast. Drowned in a sudden squall. "
        "Her poor helmsman Barnaby still haunts the drowned hold. If you take a rowboat out there, watch for his restless spirit.\""
    )
    options = (
        {"desc": "I will explore the wreck.", "goto": None}
    )
    return text, options


def morgan_siren_tips(caller):
    plugs = create_object(
        Object,
        key="Beeswax Earplugs",
        location=caller,
        aliases=["earplugs", "plugs", "beeswax"],
        tags=["eldoria_world"]
    )
    plugs.db.desc = "Dense plugs of scented amber beeswax that muffle enchanting melodies and siren songs."

    text = (
        "Morgan grunts knowingly:\n\n"
        "\"Lorelei's song will draw you straight onto the barnacle spikes! "
        "Stuff these |wBeeswax Earplugs|n in your ears before stepping into the sea cavern! "
        "Once her song can't hypnotize you, she's willing to trade rare aquatic relics for shiny surface trinkets!\""
    )
    options = (
        {"desc": "Thank you for the earplugs, Captain.", "goto": None}
    )
    return text, options


def drowned_barnaby_start_node(caller):
    has_compass = any("compass" in i.key.lower() for i in caller.contents)

    text = (
        "|cDeckhand Barnaby's Ghost|n stands beside the barnacle-covered ship wheel, water dripping "
        "silently from his spectral pea coat.\n\n"
        "\"Lost our heading... driven onto the reef in the fog... where is my compass?\""
    )
    options = []
    if has_compass:
        options.append({
            "desc": "I salvaged your Barnacled Brass Compass from the captain's quarters! [Return Compass]",
            "goto": "drowned_compass_turnin"
        })
    else:
        options.append({
            "desc": "Where did you last see the compass, Barnaby?",
            "goto": "drowned_compass_lore"
        })

    options.append({"desc": "Rest in peace, sailor.", "goto": None})
    return text, tuple(options)


def drowned_compass_lore(caller):
    return (
        "\"It slipped from my hands as the hull shattered... trapped inside the flooded captain's locker below deck...\"",
        ({"desc": "I will search for it.", "goto": None},)
    )


def drowned_compass_turnin(caller):
    caller.db.returned_compass = True
    compass = next((i for i in caller.contents if "compass" in i.key.lower()), None)
    if compass:
        compass.db.is_active = True
        compass.db.desc = (
            "A magnetized brass nautical compass radiating spectral blue energy. "
            "The enchanted needle spins and points unerringly toward hidden buried treasure!"
        )

    text = (
        "Barnaby touches the compass with glowing fingers. A peaceful aura washes over his face.\n\n"
        "\"The compass... she points true again. Keep it, voyager. May she guide your ship through all perils!\"\n\n"
        "The ghost fades into the sea mist with a final grateful wave."
    )
    options = (
        {"desc": "Farewell, helmsman.", "goto": None}
    )
    return text, options


def lorelei_start_node(caller):
    has_plugs = any("earplug" in i.key.lower() for i in caller.contents)

    text = (
        "|cLorelei the Sea Siren|n combs her sea-green hair upon an emerald tidal rock, "
        "her scales shimmering with rainbow iridescence. She sings a melody of haunting beauty.\n\n"
        "\"Wanderer of the dry lands... do you listen to the songs of the deep?\""
    )
    options = [
        {"desc": "I come in peace, Lorelei. Can we trade?", "goto": "lorelei_trade"},
        {"desc": "Step back into the sea spray.", "goto": None}
    ]
    return text, tuple(options)


def lorelei_trade(caller):
    tear = create_object(
        Object,
        key="Vial of Siren's Tear",
        location=caller,
        aliases=["tear", "vial", "siren's tear"],
        tags=["eldoria_world"]
    )
    tear.db.desc = "A luminescent pearl vial containing an enchanted tear that grants breathing and agility underwater."
    tear.db.is_drinkable = True
    tear.db.drink_type = "elixir"

    text = (
        "Lorelei smiles with aquatic grace:\n\n"
        "\"Few mortals walk into my grotto without losing their minds to the surf. "
        "Take this |wVial of Siren's Tear|n. Drink it, and the oceans shall welcome you as kin.\""
    )
    options = (
        {"desc": "Thank you, Siren of the Reef.", "goto": None}
    )
    return text, options


# =============================================================================
# 18. FEYWILD GLADE (Queen Tatiana, Oakhaven the Treant, Puck)
# =============================================================================

def tatiana_start_node(caller):
    has_moonbeam = caller.db.captured_moonbeam
    completed = caller.db.tatiana_rewarded

    text = (
        "|cQueen Tatiana of the Briar|n hovers on gossamer dragonfly wings, crowned with glowing honeysuckle. "
        "Her tiny court of pixies showers shimmering silver dust into the air.\n\n"
        "\"A mortal steps into the Court of Twilight! How delightful! Do you dance, or do you bring gifts of the moon?\""
    )
    options = []
    if not completed and not has_moonbeam:
        options.append({
            "desc": "How can I earn the favor of the Pixie Court, Your Majesty?",
            "goto": "tatiana_moonbeam_offer"
        })
    elif has_moonbeam and not completed:
        options.append({
            "desc": "I captured a swirl of pure moonlight in a crystal phial! [Present Moonbeam]",
            "goto": "tatiana_turnin"
        })
    elif completed:
        options.append({
            "desc": "The glade is magical tonight, Queen Tatiana.",
            "goto": "tatiana_aftermath"
        })

    options.append({"desc": "Bow respectfully to the tiny monarch.", "goto": None})
    return text, tuple(options)


def tatiana_moonbeam_offer(caller):
    text = (
        "Tatiana claps her tiny hands with delight:\n\n"
        "\"The moonbeams pool in the center of the Twilight Glade! "
        "Use the command |wcatch moonbeam|n while standing in the glade! "
        "Bring me a bottled moonbeam, and I shall bestow upon you the |wGolden Fey Flute|n!\""
    )
    options = (
        {"desc": "I will bottle the moonlight for you!", "goto": None}
    )
    return text, options


def tatiana_turnin(caller):
    caller.db.tatiana_rewarded = True
    flute = create_object(
        Object,
        key="Golden Fey Flute",
        location=caller,
        aliases=["flute", "fey flute"],
        tags=["eldoria_world"]
    )
    flute.db.desc = "A tiny bone flute carved by wood sprites. Playing it soothes wild forest beasts and woodland animals."

    text = (
        "Tatiana uncorks the phial and lets the shimmering silver moonlight spill over her blossom throne!\n\n"
        "The pixies erupt in joyful musical laughter! She hands you the |wGolden Fey Flute|n!\n\n"
        "\"You are forever welcome in the Court of Twilight, friend of the briar!\""
    )
    options = (
        {"desc": "Thank you, Queen Tatiana!", "goto": None}
    )
    return text, options


def tatiana_aftermath(caller):
    return "\"Play your flute whenever the wild woods threaten you! Fairies keep their promises!\"", None


def oakhaven_start_node(caller):
    cleansed = caller.db.cleansed_treant

    text = (
        "|cOakhaven the Treant|n, a colossal weeping willow with deep, wise mossy bark eyes, "
        "rustles his canopy in the twilight breeze.\n\n"
        "\"HOOOOOOOM... WHO TREADS UPON THE ANCIENT ROOTS...?\""
    )
    options = []
    if not cleansed:
        options.append({
            "desc": "Are you in pain, ancient one?",
            "goto": "oakhaven_disease"
        })
    else:
        options.append({
            "desc": "How are your branches feeling, Oakhaven?",
            "goto": "oakhaven_healed"
        })

    options.append({"desc": "Rest in peace, elder of the woods.", "goto": None})
    return text, tuple(options)


def oakhaven_disease(caller):
    text = (
        "The ancient tree groans with wooden sorrow:\n\n"
        "\"A BLACK FUNGAL ROT CREEPS ACROSS MY BASE... SAPPING THE SAP OF LIFE...\n\n"
        "MORTAL SOUL... USE THE COMMAND |wcleanse roots|n WITH CONSECRATED DAWN WATER "
        "TO PURIFY MY BARK, AND I SHALL GRANT THEE NATURE'S LIVING SHIELD!\""
    )
    options = (
        {"desc": "I will cleanse your roots, Oakhaven! (Use: cleanse roots)", "goto": None}
    )
    return text, options


def oakhaven_healed(caller):
    if not caller.db.received_bark_armor:
        caller.db.received_bark_armor = True
        armor = create_object(
            Object,
            key="Living Bark Armor",
            location=caller,
            aliases=["armor", "bark armor", "living armor"],
            tags=["eldoria_world"]
        )
        armor.db.desc = "A cuirass woven of living petrified oak that slowly regenerates its wearer's health in sunlight."

    text = (
        "\"THE SAP FLOWS SWEET AND PURE ONCE MORE! NATURE REJOICES!\n\n"
        "TAKE THIS |wLiving Bark Armor|n AS MY LIVING GIFT TO THEE, GUARDIAN OF THE GROVE!\""
    )
    options = (
        {"desc": "Thank you, elder tree.", "goto": None}
    )
    return text, options


def puck_start_node(caller):
    text = (
        "|cPuck the Jester Sprite|n sits upside down on a floating toadstool, juggling three glowing acorns.\n\n"
        "\"Riddles in the dark, riddles in the day! Answer my riddle or I'll turn your shoes to clay!\""
    )
    options = (
        {"desc": "\"I have cities, but no houses; forests, but no trees; water, but no fish. What am I?\"", "goto": "puck_riddle"},
        {"desc": "I don't have time for fairy tricks, Puck.", "goto": None}
    )
    return text, options


def puck_riddle(caller):
    text = "\"Aha! What is the answer, mortal traveler?\""
    options = (
        {"desc": "A Map!", "goto": "puck_correct"},
        {"desc": "A Dream!", "goto": "puck_wrong"},
        {"desc": "A Mirror!", "goto": "puck_wrong"},
    )
    return text, options


def puck_correct(caller):
    dust = create_object(
        Object,
        key="Bottle of Pixie Dust",
        location=caller,
        aliases=["dust", "pixie dust", "bottle"],
        tags=["eldoria_world"]
    )
    dust.db.desc = "A bottle of sparkling golden pixie dust that allows levitation over pits and chasms."

    text = (
        "Puck somersaults through the air with an ecstatic squeal!\n\n"
        "\"A Map! Smart mortal! Sharp as a thorn! Here, take this |wBottle of Pixie Dust|n! "
        "Sprinkle it over your boots when you need to walk on air! Hee-hee!\""
    )
    options = (
        {"desc": "Thanks, Puck!", "goto": None}
    )
    return text, options


def puck_wrong(caller):
    return "\"BZZZT! Wrong! It's a map! Try again when your wits are sharper!\"", None


# =============================================================================
# 19. DEEP DWARF FOUNDRY (Cog Unit 7-B & Artificer Dueran)
# =============================================================================

def cog_start_node(caller):
    awakened = caller.db.awakened_cog

    if not awakened:
        text = (
            "|cAutomaton Unit 7-B ('Cog')|n stands inert against the assembly wall. "
            "Its brass chest compartment hangs open, revealing an empty cylindrical power socket. "
            "Use: |winsert core|n to reboot the unit."
        )
        options = (
            {"desc": "Examine the empty power core slot.", "goto": None},
        )
    else:
        text = (
            "|cAutomaton Unit 7-B ('Cog')|n hums with smooth steam pressure, its amber optic lenses glowing warmly.\n\n"
            "\"UNIT 7-B OPERATIONAL. GREETINGS, RE-BOOT COMMANDER. SYSTEM INVENTORY AND HEAVY TRANSPORT READY.\""
        )
        options = (
            {"desc": "State your function, Cog.", "goto": "cog_function"},
            {"desc": "Stand easy, Unit 7-B.", "goto": None}
        )
    return text, tuple(options)


def cog_function(caller):
    text = (
        "Cog's brass vocal grate vibrates smoothly:\n\n"
        "\"I WAS ENGINEERED BY HIGH ARTIFICER DUERAN TO HAUL REFINED MITHRIL AND SERVICE "
        "THE MAGMA FORGE. MASTER DUERAN REMAINS BOUND TO THE CORE FORGE TO THE NORTH.\""
    )
    options = (
        {"desc": "Thank you, Cog.", "goto": None}
    )
    return text, options


def dueran_start_node(caller):
    vented = caller.db.vented_steam

    text = (
        "|cGhost of High Artificer Dueran|n floats before the massive magma crucible, holding a spectral smithing tongs.\n\n"
        "\"Centuries of silence... yet the core fires of Karak-Duer still burn! Who approaches the master forge?\""
    )
    options = [
        {"desc": "How can the Great Magma Crucible be safely restarted?", "goto": "dueran_forge_lore"},
    ]
    if vented and not caller.db.dueran_rewarded:
        options.append({
            "desc": "I have vented the geothermal pressure valve! [Report Success]",
            "goto": "dueran_turnin"
        })

    options.append({"desc": "Honored to stand before dwarven greatness.", "goto": None})
    return text, tuple(options)


def dueran_forge_lore(caller):
    text = (
        "Dueran gestures toward the catwalk above the lava lake:\n\n"
        "\"The pressure in the geothermal steam pipes is critical! "
        "Ascend the catwalk to the steam pressure valve and use |wturn valve|n to vent the excess vapor! "
        "Once vented, the forge will stabilize and allow the crafting of masterwork mithril gear!\""
    )
    options = (
        {"desc": "I will vent the valve, Master Artificer!", "goto": None}
    )
    return text, options


def dueran_turnin(caller):
    caller.db.dueran_rewarded = True
    goggles = create_object(
        Object,
        key="Artificer's Thermal Goggles",
        location=caller,
        aliases=["goggles", "thermal goggles"],
        tags=["eldoria_world"]
    )
    goggles.db.desc = "Brass goggles with ruby-tinted crystal lenses, allowing clear thermal vision in pitch-black caves."

    text = (
        "The ghost of the master artificer bows with deep dwarven respect:\n\n"
        "\"The pressure is stabilized! The forge fires roar true once more!\n\n"
        "Take my |wArtificer's Thermal Goggles|n! Wear them to spot mineral veins and hidden doors in the dark! "
        "May your steel never chip!\""
    )
    options = (
        {"desc": "Thank you, Master Dueran.", "goto": None}
    )
    return text, options


# =============================================================================
# 20. FROZEN PEAKS (Titus the Hermit, Brother Kaelen, Frost Drake)
# =============================================================================

def kaelen_start_node(caller):
    has_furs = any("furs" in i.key.lower() for i in caller.contents)
    saved = caller.db.saved_kaelen

    text = (
        "|cBrother Kaelen|n shivers violently in a mountain snowdrift on Frostfang Pass, "
        "his lips pale blue with hypothermia.\n\n"
        "\"S-so c-cold... lost the trail in the b-blizzard...\""
    )
    options = []
    if not saved and has_furs:
        options.append({
            "desc": "Wrap this warm Bundle of Furs around your shoulders! [Save Kaelen]",
            "goto": "kaelen_save"
        })
    elif not saved and not has_furs:
        options.append({
            "desc": "Hold on, Brother! I will find warm furs for you!",
            "goto": None
        })
    else:
        options.append({
            "desc": "You are looking much warmer, Brother.",
            "goto": "kaelen_aftermath"
        })

    return text, tuple(options)


def kaelen_save(caller):
    furs = next((i for i in caller.contents if "furs" in i.key.lower()), None)
    if furs:
        furs.delete()
    caller.db.saved_kaelen = True

    beads = create_object(
        Object,
        key="Pilgrim's Blessed Prayer Beads",
        location=caller,
        aliases=["beads", "prayer beads"],
        tags=["eldoria_world"]
    )
    beads.db.desc = "Warm sandalwood beads blessed on the mountain shrine, offering fortitude against winter cold."

    text = (
        "You wrap the heavy bear and wolf furs tightly around Kaelen. "
        "Color slowly returns to his cheeks as he breathes a tearful sigh of relief.\n\n"
        "\"Praise the dawn! You saved my life! Take my |wPilgrim's Blessed Prayer Beads|n—they "
        "will protect you against the biting mountain frost! I am heading back to Eldoria Cathedral!\""
    )
    options = (
        {"desc": "Safe journey down the mountain, Brother.", "goto": None}
    )
    return text, options


def kaelen_aftermath(caller):
    return "\"Thanks to your warm furs, I have the strength to make the descent!\"", None


def titus_start_node(caller):
    has_lichen = any("frost-lichen" in i.key.lower() or "lichen" in i.key.lower() for i in caller.contents)

    text = (
        "|cTitus the Blind Mountain Hermit|n sits beside a crackling peat fire inside his ice cavern, "
        "stroking a snow-white owl perched upon his arm.\n\n"
        "\"I hear your footsteps in the snow, traveler. The winds whisper of your deeds.\""
    )
    options = []
    if not has_lichen:
        options.append({
            "desc": "What are you brewing over the fire, Titus?",
            "goto": "titus_brew_story"
        })
    else:
        options.append({
            "desc": "I gathered this Pinch of Frost-Lichen from the chasm cliff! [Deliver Lichen]",
            "goto": "titus_turnin"
        })

    options.append({"desc": "Stay warm by the hearth, hermit.", "goto": None})
    return text, tuple(options)


def titus_brew_story(caller):
    text = (
        "Titus inhales the steam from his iron kettle:\n\n"
        "\"I brew the ancient Seer's Frost-Tea, but I am out of |wFrost-Lichen|n. "
        "It only grows on the sheer precipice overlooking the Howling Chasm Bridge.\n\n"
        "Bring me a pinch of the frozen lichen, and I shall unveil the secret of the celestial summit!\""
    )
    options = (
        {"desc": "I will harvest the frost-lichen for you.", "goto": None}
    )
    return text, options


def titus_turnin(caller):
    lichen = next((i for i in caller.contents if "lichen" in i.key.lower()), None)
    if lichen:
        lichen.delete()

    lens = create_object(
        Object,
        key="Astral Lens Fragment",
        location=caller,
        aliases=["lens", "astral lens", "fragment"],
        tags=["eldoria_world"]
    )
    lens.db.desc = "A flawless prism of celestial crystal that focuses starlight to decipher ancient mountain monuments."

    text = (
        "Titus drops the frost-lichen into the boiling kettle. A sweet, crisp mint aroma fills the warm cave.\n\n"
        "He drinks deeply, his sightless eyes glowing with brief starlight:\n\n"
        "\"I see the summit... the sleeping Frost Drake curls around the celestial sundial. "
        "Take this |wAstral Lens Fragment|n. Slot it into the sundial to reveal the lost constellation of the ancients!\""
    )
    options = (
        {"desc": "Thank you, wise hermit.", "goto": None}
    )
    return text, options


def skirnir_start_node(caller):
    text = (
        "|cSkirnir the Frost Drake|n slumbers atop the colossal celestial sundial at the Cloud-Piercing Summit. "
        "Plumes of freezing mist puff rhythmically from his crystalline nostrils. Near his tail lies a dropped "
        "|wIce Drake's Molted Scale|n. Moving loudly might disturb his slumber!"
    )
    options = (
        {"desc": "Quietly pick up the molted scale. (get scale)", "goto": None},
        {"desc": "Back away slowly into the blizzard.", "goto": None}
    )
    return text, options


# =============================================================================
# 21. LORD ALDOUS STERLING (Royal Bank of Eldoria & Vault)
# =============================================================================

def aldous_start_node(caller):
    text = (
        "|cLord Aldous Sterling|n peers over his gold-rimmed spectacles and adjusts his velvet waistcoat.\n\n"
        "\"Welcome to the Royal Bank of Eldoria, esteemed patron. We offer secure vault storage for precious relics "
        "and physical coin deposit services. How may the House of Sterling serve you today?\""
    )
    options = (
        {"desc": "How do banking deposits and withdrawals work?", "goto": "aldous_banking_info"},
        {"desc": "How does the private safety deposit vault work?", "goto": "aldous_vault_info"},
        {"desc": "What are the currency denominations of the realm?", "goto": "aldous_currency_info"},
        {"desc": "Thank you, Lord Sterling. Good day.", "goto": None}
    )
    return text, options


def aldous_banking_info(caller):
    text = (
        "Sterling pats a stack of leather-bound account books:\n\n"
        "\"You may deposit your physical coins using |wdeposit <amount> [gold/silver/copper]|n, and "
        "withdraw them anytime with |wwithdraw <amount> [currency]|n. Check your finances at any time with |wbalance|n!\n\n"
        "Coins kept in our vaults are safe from theft and dungeon peril.\""
    )
    options = (
        {"desc": "Very clear. What else?", "goto": "aldous_start_node"},
        {"desc": "Understood.", "goto": None}
    )
    return text, options


def aldous_vault_info(caller):
    text = (
        "Sterling gestures toward the massive reinforced vault door behind him:\n\n"
        "\"Our subterranean lockers are forged of solid steel! You can place rare weapons, armor, or trophies "
        "into your private locker using |wvault store <item>|n, retrieve them with |wvault retrieve <item>|n, "
        "and inspect your locker contents with |wvault list|n!\""
    )
    options = (
        {"desc": "Splendid security. Tell me more.", "goto": "aldous_start_node"},
        {"desc": "Good to know.", "goto": None}
    )
    return text, options


def aldous_currency_info(caller):
    text = (
        "Sterling counts out a sample display of minted coins on velvet:\n\n"
        "\"The Eldorian monetary standard operates on three physical metals:\n"
        "- |rCopper (cp)|n: Daily bread, river bait, and small sundries.\n"
        "- |wSilver (sp)|n: Valued at 10 Copper coins.\n"
        "- |yGold Sovereign (gp)|n: Valued at 10 Silver (or 100 Copper). The standard for royal bounties and fine arms.\""
    )
    options = (
        {"desc": "Understood, Lord Sterling.", "goto": "aldous_start_node"},
        {"desc": "Thank you.", "goto": None}
    )
    return text, options


# =============================================================================
# MASTER SCRIBE CASSIAN (Grand Philologist & Keeper of the Scriptorium)
# =============================================================================

def cassian_start_node(caller):
    text = (
        "|cMaster Scribe Cassian|n dips an emerald-quilled pen into shimmering silver ink, "
        "adjusting his magnifying monocle over illuminated parchment scrolls.\n\n"
        "\"Welcome to the Scriptorium of Eldoria, traveler. Language is the vessel of ancient magic "
        "and mortal memory. Without understanding of the realm's sacred tongues, grimoires are mere dead leaves.\n\n"
        "How may the Scriptorium assist your studies?\""
    )
    options = [
        {"desc": "What tongues are spoken throughout Eldoria?", "goto": "cassian_tongues_overview"},
        {"desc": "Can you tutor me in a foreign language? (Gain Fluency)", "goto": "cassian_tutoring_menu"},
        {"desc": "Do you have any language primers or lexicons available?", "goto": "cassian_primers_menu"},
        {"desc": "Thank you, Master Cassian. I will study on my own.", "goto": None}
    ]
    return text, tuple(options)


def cassian_tongues_overview(caller):
    text = (
        "Cassian unrolls a grand linguistic genealogical chart upon the oak lectern:\n\n"
        "\"The known realm speaks nine grand families of tongues:\n"
        "1. |wCommon|n: The universal trade tongue created by ancient merchant leagues.\n"
        "2. |gElven|n: The lilting, harmonic cadence of the ancient woodland elders.\n"
        "3. |yDwarven|n: Stone-hewn, guttural consonants forged in subterranean halls.\n"
        "4. |mDrow|n: Whispered, venomous sibilants used in the Underdark.\n"
        "5. |rDraconic|n: Thunderous flame-syllables dating back to the First Wyrms.\n"
        "6. |cCelestial|n: The choral resonance of the sun and celestial spheres.\n"
        "7. |yCentaur|n: Rhythmic, galloping dialects of the wind-swept steppes.\n"
        "8. |wHalfling|n: Rapid, cheerful idioms of countryside homesteads.\n"
        "9. |gGoblinoid|n: Snarling, guttural gutter-speak of raiders and scavengers.\n\n"
        "To view your own fluency at any time, simply type |wlanguages|n.\""
    )
    options = [
        {"desc": "Tell me about academic study and practice.", "goto": "cassian_study_lore"},
        {"desc": "Return to the main menu.", "goto": "cassian_start_node"}
    ]
    return text, tuple(options)


def cassian_study_lore(caller):
    text = (
        "\"You may study right here at the desks of this Scriptorium! "
        "As long as you are seated within this library, you can type |wstudylang <language>|n "
        "(or |wpractice <language>|n) to review grammar rules and gain fluency.\n\n"
        "Furthermore, if you carry a dedicated Language Primer or Lexicon in your pack, "
        "you can study wherever you rest in your travels!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "cassian_start_node"}
    ]
    return text, tuple(options)


def cassian_tutoring_menu(caller):
    text = (
        "\"I can offer formal philological instruction in several classical tongues. "
        "Each session requires mental stamina and dedication, but will steadily improve your vocabulary.\n\n"
        "Which tongue would you like to practice?\""
    )
    options = [
        {"desc": "Practice Elven (The Lilting Tongue)", "goto": ("cassian_tutor_exec", {"lang": "elven"})},
        {"desc": "Practice Dwarven (The Runestone Tongue)", "goto": ("cassian_tutor_exec", {"lang": "dwarven"})},
        {"desc": "Practice Draconic (The Flame-Speech)", "goto": ("cassian_tutor_exec", {"lang": "draconic"})},
        {"desc": "Practice Celestial (The Sacred Chant)", "goto": ("cassian_tutor_exec", {"lang": "celestial"})},
        {"desc": "Practice Goblinoid (The Skulker Dialect)", "goto": ("cassian_tutor_exec", {"lang": "goblinoid"})},
        {"desc": "Return to the main menu.", "goto": "cassian_start_node"}
    ]
    return text, tuple(options)


def cassian_tutor_exec(caller, raw_string, **kwargs):
    lang = kwargs.get("lang", "elven")
    from world.languages import LANGUAGES
    l_name = LANGUAGES.get(lang, {}).get("name", lang.title())

    if (caller.db.stamina or 0) < 15:
        return "\"You are too fatigued for scholarly discipline! Rest a moment and restore your stamina.\"", (
            {"desc": "Return to the main menu.", "goto": "cassian_start_node"},
        )

    caller.db.stamina -= 15
    langs = caller.db.languages or {}
    curr = langs.get(lang, 0)
    gain = 5
    langs[lang] = min(100, curr + gain)
    caller.db.languages = langs

    text = (
        f"Master Scribe Cassian drills you through the declensions, accents, and idiom structure of |c{l_name}|n.\n\n"
        f"|g*** TUTORING SESSION COMPLETE ***|n\n"
        f"Your fluency in {l_name} rises from |w{curr}%|n to |g{langs[lang]}%|n! (Cost: 15 Stamina)\n\n"
        f"\"Well done, pupil. Repeat these drills often, or practice speaking with native speakers in the realm!\""
    )
    options = [
        {"desc": "Practice another tongue.", "goto": "cassian_tutoring_menu"},
        {"desc": "Return to the main menu.", "goto": "cassian_start_node"}
    ]
    return text, tuple(options)


def cassian_primers_menu(caller):
    has_primer = any("primer" in i.key.lower() or "lexicon" in i.key.lower() for i in caller.contents)
    if has_primer:
        text = (
            "\"You already carry a scholarly language text in your inventory! "
            "Study it diligently using |wstudylang <language>|n wherever you travel!\""
        )
        options = [
            {"desc": "Return to the main menu.", "goto": "cassian_start_node"}
        ]
        return text, tuple(options)

    from evennia.utils.create import create_object
    from typeclasses.objects import Object
    primer = create_object(
        Object,
        key="Elven Grammar Primer",
        location=caller,
        aliases=["primer", "elven primer", "lexicon"],
        tags=["eldoria_world"]
    )
    primer.db.desc = "An illuminated grammar primer bound in soft deer-hide detailing Elven verbs and vocabulary."

    text = (
        "Cassian hands you an illuminated volume bound in green deer-hide:\n\n"
        "\"Here is a copy of the |wElven Grammar Primer|n from our scriptorium collection. "
        "Keep it safe in your pack. You can use |wstudylang elven|n at any campfire to practice!\""
    )
    options = [
        {"desc": "Thank you, Master Scribe.", "goto": "cassian_start_node"}
    ]
    return text, tuple(options)


# =============================================================================
# MARITIME FERRY OPERATORS & ISLAND NPCS
# =============================================================================

def maeve_start_node(caller):
    text = (
        "|cFerrywoman Maeve|n, a sun-weathered sailor with sea-salt in her braided auburn hair, "
        "coils a heavy hemp mooring rope on the pier bollard.\n\n"
        "\"Fair winds, traveler! The Salt-Spit Sea Ferry is ready to sail. "
        "Whether you're bound for the rugged sands of Dead Man's Cove or the uncharted wilds "
        "of the |yIsle of Serpents|n, my caravel will get you there in one piece.\""
    )
    options = [
        {"desc": "Where do you sail, and what are the fares?", "goto": "maeve_routes_info"},
        {"desc": "How do the Crown maritime taxes work?", "goto": "maeve_tax_info"},
        {"desc": "How do I board your ship?", "goto": "maeve_board_info"},
        {"desc": "Safe sailing, Maeve.", "goto": None}
    ]
    return text, tuple(options)


def maeve_routes_info(caller):
    text = (
        "Maeve taps a brass compass against her sea-chart:\n\n"
        "\"From these docks, I run two regular crossings:\n"
        "- |cDead Man's Cove|n: 20 Copper (2 Silver). A swift trip across the bay to the smuggler coast.\n"
        "- |yCorsair's Anchorage (Isle of Serpents)|n: 50 Copper (5 Silver). An open-ocean crossing to the remote tropical island.\n\n"
        "You can check current fares any time by typing |wfare <destination>|n!\""
    )
    options = [
        {"desc": "Tell me about the municipal tax.", "goto": "maeve_tax_info"},
        {"desc": "Return to the main menu.", "goto": "maeve_start_node"}
    ]
    return text, tuple(options)


def maeve_tax_info(caller):
    text = (
        "Maeve gives a wry grin and nods toward the royal citadel:\n\n"
        "\"By royal charter of Lord Aldous Sterling and the Crown Council, all passenger vessels pay a "
        "|wtwenty percent municipal tariff|n directly into Eldoria's Royal Coffers.\n\n"
        "Every time you buy a ticket, twenty percent of your copper, silver, or gold goes to city coffers "
        "to pay for harbour dredging, breakwater repairs, and lighthouse oil! "
        "You can inspect the city coffers anytime at the Royal Bank using |wcoffers|n.\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "maeve_start_node"}
    ]
    return text, tuple(options)


def maeve_board_info(caller):
    text = (
        "\"Whenever you're ready with coin in your pocket, simply type:\n"
        "  |wboard island|n (to sail to the Isle of Serpents)\n"
        "  |wboard cove|n (to cross the bay to Dead Man's Cove)\n\n"
        "My crew will cast off the lines and we'll catch the turning tide!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "maeve_start_node"}
    ]
    return text, tuple(options)


def jacques_start_node(caller):
    text = (
        "|cOld Riverman Jacques|n leans on an iron-shod cedar push pole, chewing on sweet marsh grass.\n\n"
        "\"Watch your footing near the reeds, friend. The river currents run fast and deep here. "
        "If you're seeking good fishing or quiet solitude, I can punt you out to the |wWhispering Silt Islet|n.\""
    )
    options = [
        {"desc": "Tell me about the Whispering Silt Islet.", "goto": "jacques_islet_lore"},
        {"desc": "What is the fare to cross?", "goto": "jacques_fare_info"},
        {"desc": "Good day, Jacques.", "goto": None}
    ]
    return text, tuple(options)


def jacques_islet_lore(caller):
    text = (
        "Jacques gestures toward the middle of the rushing foam:\n\n"
        "\"That islet has stood in the river fork since the First Age. An ancient weeping willow grows there, "
        "and legendary golden trout feed in the calm eddies behind the sandbar. You can't reach it on foot—only my flatboat can navigate the rocks!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "jacques_start_node"}
    ]
    return text, tuple(options)


def jacques_fare_info(caller):
    text = (
        "\"A modest fifteen copper pennies (or one silver and five copper) gets you passage there and back. "
        "Three copper of that goes straight into Lord Sterling's royal coffer! Type |wboard islet|n when you want to cross.\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "jacques_start_node"}
    ]
    return text, tuple(options)


def joshua_start_node(caller):
    text = (
        "|cHelmsman Joshua|n tests the tension on a heavy leather-wrapped oar resting against the longboat gunwale.\n\n"
        "\"Welcome to Corsair's Anchorage, mate. The Isle of Serpents is wild and treacherous. "
        "If you want to skirt the sharp volcanic reefs without hiking through the jungle, my longboat "
        "can row you to the |cSmuggler's Lagoon|n or the |rLeviathan's Graveyard|n.\""
    )
    options = [
        {"desc": "What routes do you row?", "goto": "joshua_routes_info"},
        {"desc": "Tell me about the Leviathan's Graveyard.", "goto": "joshua_graveyard_lore"},
        {"desc": "Keep watch, Joshua.", "goto": None}
    ]
    return text, tuple(options)


def joshua_routes_info(caller):
    text = (
        "Joshua points out across the turquoise breakers:\n\n"
        "\"I can row you along the island coast:\n"
        "- |cSmuggler's Lagoon|n: 25 Copper. Sheltered waters concealed behind a natural sea arch.\n"
        "- |rLeviathan's Graveyard|n: 30 Copper. The reef where the imperial galleon H.M.S. Sovereign met her doom.\n\n"
        "Type |wboard lagoon|n or |wboard wreck|n to climb aboard!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "joshua_start_node"}
    ]
    return text, tuple(options)


def joshua_graveyard_lore(caller):
    text = (
        "\"A violent storm threw the royal treasure galleon H.M.S. Sovereign straight onto the black basalt fangs. "
        "Her timbers are shattered across the shallows, and Captain Flint was marooned on the beach. "
        "Watch out for deep-sea serpents if you dive near the shattered hold!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "joshua_start_node"}
    ]
    return text, tuple(options)


def flint_start_node(caller):
    text = (
        "|cCaptain 'Salt-Beard' Flint|n, clad in a tattered bicorne hat and a salt-bleached velvet coat, "
        "carves a piece of driftwood with a tarnished oyster knife.\n\n"
        "\"Ahoy, land-strider. You're looking at the captain of the finest sovereign galleon that ever sailed—until "
        "the Siren's reef tore her keel in two! Now I rule these bleached sands and whale bones.\""
    )
    options = [
        {"desc": "Is there any treasure left in the wreck of the Sovereign?", "goto": "flint_treasure_lore"},
        {"desc": "How can I survive the island's reefs?", "goto": "flint_diving_advice"},
        {"desc": "Farewell, Captain Flint.", "goto": None}
    ]
    return text, tuple(options)


def flint_treasure_lore(caller):
    text = (
        "Flint winks with a weathered, salt-crusted eye:\n\n"
        "\"My iron-bound captain's strongbox still rests among the submerged ribs of the shattered hull in the "
        "Leviathan's Graveyard! If you're brave enough to wade into the surf, it's yours. "
        "Just keep an eye out for tiger barracudas and sea drakes!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "flint_start_node"}
    ]
    return text, tuple(options)


def flint_diving_advice(caller):
    text = (
        "\"Deep inside the Glowing Coral Grotto on the east side of the island lives Shelly, a strange hermit. "
        "She knows how to craft a Glow-Pearl Diving Mask from bioluminescent oysters. "
        "With one of those, you can see crystal clear through the foaming tides!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "flint_start_node"}
    ]
    return text, tuple(options)


def shelly_start_node(caller):
    has_pearl = any("pearl" in i.key.lower() for i in caller.contents)
    has_mask = any("mask" in i.key.lower() for i in caller.contents)

    text = (
        "|cCoral Hermit Shelly|n sits cross-legged upon a quartz ledge beside a tide pool, "
        "weaving dried kelp strands and iridescent mother-of-pearl into intricate talismans.\n\n"
        "\"Listen closely... do you hear the heartbeat of the deep trench? The coral polyps whisper secrets "
        "to those who bring offerings of the sea.\""
    )
    options = []
    if has_pearl and not has_mask:
        options.append({
            "desc": "I have a rare pearl! Can you craft a diving mask?",
            "goto": "shelly_craft_mask"
        })
    else:
        options.append({
            "desc": "What do the coral polyps whisper?",
            "goto": "shelly_coral_lore"
        })

    options.append({"desc": "May the tides be gentle, Shelly.", "goto": None})
    return text, tuple(options)


def shelly_craft_mask(caller):
    # Consume pearl and give mask
    for item in caller.contents:
        if "pearl" in item.key.lower():
            item.delete()
            break

    from evennia.utils.create import create_object
    from typeclasses.objects import Object
    mask = create_object(
        Object,
        key="Glow-Pearl Diving Mask",
        location=caller,
        aliases=["mask", "diving mask", "pearl mask"],
        tags=["eldoria_world"]
    )
    mask.db.desc = "A waterproof face mask sculpted from sea-tortoise shell and inlaid with twin luminescent glow-pearls."
    mask.db.slot = "head"

    text = (
        "Shelly takes the glowing pearl, chants an archaic song of the tides, and embeds it into a polished sea-shell frame:\n\n"
        "\"Take this |wGlow-Pearl Diving Mask|n, child of the dry land. "
        "Wear it upon your brow, and the darkest depths of the ocean shall be bright as morning sunlight!\""
    )
    options = [
        {"desc": "Thank you, Shelly.", "goto": None}
    ]
    return text, tuple(options)


def shelly_coral_lore(caller):
    text = (
        "\"The Sunken Temple of the Sea Serpent lies half-drowned to the south. "
        "Within its abalone sanctuary rests an ancient Coral Harpoon, blessed by the sea gods. "
        "Only those who understand the tides can claim it!\""
    )
    options = [
        {"desc": "Return to the main menu.", "goto": "shelly_start_node"}
    ]
    return text, tuple(options)
