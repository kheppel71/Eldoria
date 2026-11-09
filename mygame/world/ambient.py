"""
Ambient World Script
Periodically breathes life into Eldoria with atmospheric room messages and events.
"""

import random
from evennia.scripts.scripts import DefaultScript
from evennia.objects.models import ObjectDB


AMBIENT_EVENTS = {
    "Eldoria Grand Plaza": [
        "The great wyrm fountain pulses with crystalline light, sending a delicate, refreshing mist across the marble plaza.",
        "A flock of white doves flutters down from the rooftops, landing briefly near the fountain before scattering into the blue sky.",
        "A soft chime rings out from the cathedral towers to the west, echoing harmoniously off the surrounding stone buildings."
    ],
    "The Sunken Bazaar": [
        "A spice merchant calls out enthusiastically, offering free pinches of fragrant saffron and roasted almonds to passing travelers.",
        "A sudden gust of wind flutters the colorful silk awnings above the market stalls.",
        "The delicious aroma of sweet fried dough and honey wafts from a baker's cart."
    ],
    "The Drunken Dragon Tavern": [
        "A chorus of raucous laughter erupts from a corner table as patrons toast with heavy clay flagons of mead.",
        "The bard tunes a wooden lute by the hearth and begins singing a jaunty ballad about fallen dragons.",
        "Barnaby swiftly catches a tumbling tankard with a seasoned grin, not spilling a single drop."
    ],
    "Thunderhammer Forge": [
        "Gorim brings his heavy hammer down with a deafening *CLANG*, showering the flagstones in an arc of fiery orange sparks.",
        "A billow of black soot and blistering heat rolls out from the furnace as the bellows groan."
    ],
    "The Silver Crucible Apothecary": [
        "A delicate glass alembic bubbles vigorously, releasing a coil of sweet, lavender-scented vapor toward the ceiling.",
        "Madam Belladonna adjusts the brass weights on her balance scale with practiced precision."
    ],
    "The Whispering Woods": [
        "A cool autumn wind sighs through the ancient boughs, sending a gentle shower of golden leaves drifting downward.",
        "In the shadowed undergrowth, a pair of curious golden eyes gleams for a heartbeat before vanishing silently.",
        "A woodpecker drums rhythmically against a hollow birch tree in the distance."
    ],
    "The Sunken Mire": [
        "A bubble of swamp gas breaks the surface of the black water with a hollow *bloop*, releasing a pale, luminescent vapor.",
        "A chorus of deep-throated bullfrogs croaks in the dense reeds, abruptly falling silent as a shadow flits overhead.",
        "Faint will-o'-the-wisps dance lazily across the distant mist."
    ],
    "Dusty Antechamber": [
        "A freezing draft sweeps through the corridor, making the shadows cast by the torches flicker wildly.",
        "From somewhere deep within the mountain stone comes a faint, rhythmic scraping... like bone against granite."
    ],
    "Sanctum of the Hollow King": [
        "The spectral blue flames lining the obsidian walls flare with sudden, icy intensity.",
        "A low, chilling murmur whispers through the hall, ancient and laden with sorrow."
    ],
    "Sewer Sluice Gate": [
        "Rushing wastewater churns beneath the iron grating, carrying the scent of damp moss and rain runoff.",
        "A chorus of distant rat squeaks echoes down the brick tunnel system."
    ],
    "Dead Man's Cove": [
        "Foaming breakers crash violently against the offshore reef, sending a salty white spray into the sea air.",
        "A mournful gull circles high above the splintered masts of the frigate wreck."
    ],
    "Twilight Moonlit Glade": [
        "A cluster of bioluminescent toadstools pulses with soft lilac light as fairy giggles ring out.",
        "Silver moonlight ripples across the grass like liquid silk beneath the weeping branches."
    ],
    "The Core Magma Forge": [
        "A subterranean geyser of molten lava bubbles and pops, splashing bright orange magma against obsidian walls.",
        "The great brass steam pipes groan under rhythmic, pressurized heartbeats."
    ],
    "Frostfang Mountain Pass": [
        "A howling gale of sub-zero wind whips ice needles across the sheer cliff trail.",
        "Far below in the chasm, the groaning grind of ancient glacier ice rumbles like distant thunder."
    ]
}


class AmbientWorldScript(DefaultScript):
    """
    A global background script that injects atmospheric flavor into Eldoria.
    """

    def at_script_creation(self):
        self.key = "ambient_world_script"
        self.desc = "Breathes ambient atmospheric life into Eldoria."
        self.interval = 45  # Fire every 45 seconds
        self.persistent = True

    def at_repeat(self):
        """
        Called every self.interval seconds.
        Picks active rooms and messages players inside them.
        """
        for room_name_substr, messages in AMBIENT_EVENTS.items():
            matching_rooms = ObjectDB.objects.filter(
                db_tags__db_key="eldoria_world",
                db_key__icontains=room_name_substr
            )
            for room in matching_rooms:
                # Only broadcast if there are actual players present
                has_players = any(c.has_account for c in room.contents if hasattr(c, "has_account"))
                if has_players:
                    msg = random.choice(messages)
                    room.msg_contents(f"|y{msg}|n")

