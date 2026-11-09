"""
Nightmare LPmud Socials & Feelings Soul Engine.

Implements:
1. Dynamic Soul registry with directed and undirected perspective messages.
2. Contextual adverbs support ('nod sagely at <target>', 'glare menacingly').
3. Directory of available social feelings ('feelings' / 'socials').
"""

SOCIALS_TABLE = {
    "nod": {
        "self_no_target": "You nod in agreement.",
        "room_no_target": "{caller} nods in agreement.",
        "self_target": "You nod {adverb}at {target}.",
        "target": "{caller} nods {adverb}at you.",
        "room_target": "{caller} nods {adverb}at {target}."
    },
    "bow": {
        "self_no_target": "You bow with deep respect.",
        "room_no_target": "{caller} bows with deep respect.",
        "self_target": "You bow {adverb}before {target}.",
        "target": "{caller} bows {adverb}before you.",
        "room_target": "{caller} bows {adverb}before {target}."
    },
    "hug": {
        "self_no_target": "You look around yearning for a warm hug.",
        "room_no_target": "{caller} looks around yearning for a hug.",
        "self_target": "You wrap your arms around {target} in a warm hug.",
        "target": "{caller} wraps their arms around you in a warm hug.",
        "room_target": "{caller} wraps their arms around {target} in a warm hug."
    },
    "glare": {
        "self_no_target": "You glare with icy irritation.",
        "room_no_target": "{caller} glares with icy irritation.",
        "self_target": "You glare {adverb}at {target}.",
        "target": "{caller} glares {adverb}at you.",
        "room_target": "{caller} glares {adverb}at {target}."
    },
    "smirk": {
        "self_no_target": "A sly smirk spreads across your face.",
        "room_no_target": "A sly smirk spreads across {caller}'s face.",
        "self_target": "You smirk {adverb}at {target}.",
        "target": "{caller} smirks {adverb}at you.",
        "room_target": "{caller} smirks {adverb}at {target}."
    },
    "cower": {
        "self_no_target": "You cower in fearful terror!",
        "room_no_target": "{caller} cowers in fearful terror!",
        "self_target": "You cower {adverb}before {target}!",
        "target": "{caller} cowers {adverb}before you!",
        "room_target": "{caller} cowers {adverb}before {target}!"
    },
    "cheer": {
        "self_no_target": "You cheer enthusiastically: 'Hooray!'",
        "room_no_target": "{caller} cheers enthusiastically: 'Hooray!'",
        "self_target": "You cheer {adverb}for {target}!",
        "target": "{caller} cheers {adverb}for you!",
        "room_target": "{caller} cheers {adverb}for {target}!"
    },
    "shrug": {
        "self_no_target": "You shrug noncommittally.",
        "room_no_target": "{caller} shrugs noncommittally.",
        "self_target": "You shrug {adverb}at {target}.",
        "target": "{caller} shrugs {adverb}at you.",
        "room_target": "{caller} shrugs {adverb}at {target}."
    },
    "applaud": {
        "self_no_target": "You applaud enthusiastically.",
        "room_no_target": "{caller} applauds enthusiastically.",
        "self_target": "You applaud {adverb}for {target}.",
        "target": "{caller} applauds {adverb}for you.",
        "room_target": "{caller} applauds {adverb}for {target}."
    },
    "wink": {
        "self_no_target": "You wink suggestively.",
        "room_no_target": "{caller} winks suggestively.",
        "self_target": "You wink {adverb}at {target}.",
        "target": "{caller} winks {adverb}at you.",
        "room_target": "{caller} winks {adverb}at {target}."
    },
    "giggle": {
        "self_no_target": "You giggle with amusement.",
        "room_no_target": "{caller} giggles with amusement.",
        "self_target": "You giggle {adverb}at {target}.",
        "target": "{caller} giggles {adverb}at you.",
        "room_target": "{caller} giggles {adverb}at {target}."
    },
    "salute": {
        "self_no_target": "You snap a crisp, disciplined military salute.",
        "room_no_target": "{caller} snaps a crisp military salute.",
        "self_target": "You snap a sharp salute {adverb}to {target}.",
        "target": "{caller} snaps a sharp military salute {adverb}to you.",
        "room_target": "{caller} snaps a sharp military salute {adverb}to {target}."
    },
    "sigh": {
        "self_no_target": "You heave a deep, weary sigh.",
        "room_no_target": "{caller} heaves a deep, weary sigh.",
        "self_target": "You sigh {adverb}at {target}.",
        "target": "{caller} sighs {adverb}at you.",
        "room_target": "{caller} sighs {adverb}at {target}."
    }
}


def execute_social(caller, verb, args_text=""):
    """
    Parses and executes a social feeling with optional target and adverb.
    """
    data = SOCIALS_TABLE.get(verb.lower())
    if not data:
        return False, f"Unknown social verb '{verb}'."

    loc = caller.location
    if not loc:
        return False, "You are floating in the void."

    # Parse target and adverb
    # e.g., "sagely at Player" or "Player" or "happily"
    target = None
    adverb_str = ""

    tokens = args_text.strip().split() if args_text else []
    if "at" in tokens:
        at_idx = tokens.index("at")
        adverb_tokens = tokens[:at_idx]
        target_tokens = tokens[at_idx + 1:]
        if adverb_tokens:
            adverb_str = " ".join(adverb_tokens) + " "
        if target_tokens:
            target = caller.search(" ".join(target_tokens), location=loc)
            if not target:
                return False, "Target not found."
    elif tokens:
        # Try target first
        target = caller.search(" ".join(tokens), location=loc)
        if not target:
            # Treat as pure adverb
            adverb_str = " ".join(tokens) + " "

    c_name = caller.key
    t_name = target.key if target else ""

    if target:
        msg_self = data["self_target"].format(caller=c_name, target=t_name, adverb=adverb_str)
        msg_target = data["target"].format(caller=c_name, target=t_name, adverb=adverb_str)
        msg_room = data["room_target"].format(caller=c_name, target=t_name, adverb=adverb_str)

        caller.msg(f"|y{msg_self}|n")
        target.msg(f"|Y{msg_target}|n")
        loc.msg_contents(f"|y{msg_room}|n", exclude=[caller, target])
    else:
        msg_self = data["self_no_target"].format(caller=c_name, adverb=adverb_str)
        msg_room = data["room_no_target"].format(caller=c_name, adverb=adverb_str)

        caller.msg(f"|y{msg_self}|n")
        loc.msg_contents(f"|y{msg_room}|n", exclude=[caller])

    return True, "Executed."

