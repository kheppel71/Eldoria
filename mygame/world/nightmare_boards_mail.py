"""
Nightmare LPmud Bulletin Board & Courier Post Office System.

Implements:
1. Room-based Persistent Bulletin Boards (post, read, list, remove).
2. Postal Mail & Parcel Delivery between players (letters, coin enclosures).
"""

import time
from evennia.objects.models import ObjectDB


# =============================================================================
# 1. BULLETIN BOARDS
# =============================================================================

def get_room_board(room):
    """Retrieves or initializes the message board on a room."""
    if not hasattr(room, "db"):
        return []
    if room.db.bulletin_board is None:
        room.db.bulletin_board = []
    return room.db.bulletin_board


def post_to_board(room, author_name, subject, message):
    """Posts a new note to the room's bulletin board."""
    board = get_room_board(room)
    note_id = len(board) + 1
    note = {
        "id": note_id,
        "author": author_name,
        "subject": subject.strip() or "Untitled Notice",
        "message": message.strip(),
        "date": time.strftime("%Y-%m-%d %H:%M")
    }
    board.append(note)
    room.db.bulletin_board = board

    room.msg_contents(
        f"|y{author_name} pins a new parchment notice to the board: '{note['subject']}'.|n"
    )
    return True, f"Note #{note_id} posted successfully!"


def read_board_note(room, note_id):
    """Reads a specific note from the room's board."""
    board = get_room_board(room)
    for n in board:
        if n["id"] == note_id:
            return n
    return None


def remove_board_note(room, note_id, remover):
    """Removes a note if remover is the author or a wizard."""
    board = get_room_board(room)
    for i, n in enumerate(board):
        if n["id"] == note_id:
            if n["author"].lower() != remover.key.lower() and not remover.permissions.get("Wizards"):
                return False, "You can only remove your own notices from the board."
            board.pop(i)
            # Re-index
            for idx, item in enumerate(board):
                item["id"] = idx + 1
            room.db.bulletin_board = board
            return True, f"Notice #{note_id} has been removed from the board."
    return False, f"Notice #{note_id} was not found on the board."


# =============================================================================
# 2. COURIER POST OFFICE & MAIL SYSTEM
# =============================================================================

def init_mailbox(char):
    """Ensures player has a mailbox structure."""
    if not hasattr(char, "db"):
        return
    if char.db.mailbox is None:
        char.db.mailbox = []


def send_mail(sender, recipient, subject, body, gold=0):
    """Sends a letter and optional gold coin enclosure to recipient."""
    init_mailbox(recipient)

    if gold > 0:
        s_coins = sender.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        if s_coins.get("gold", 0) < gold:
            return False, f"You do not have {gold} Gold to enclose in this letter."
        s_coins["gold"] -= gold
        sender.db.coins = s_coins

    letter = {
        "id": len(recipient.db.mailbox) + 1,
        "from": sender.key,
        "subject": subject.strip() or "A Sealed Letter",
        "body": body.strip(),
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "enclosed_gold": gold,
        "read": False
    }

    mbox = recipient.db.mailbox or []
    mbox.append(letter)
    recipient.db.mailbox = mbox

    recipient.msg(f"\n|Y*** A city courier hands you a sealed letter from {sender.key}! (Type: |wmailbox|Y) ***|n\n")
    return True, f"Your letter to {recipient.key} has been dispatched by courier!"

