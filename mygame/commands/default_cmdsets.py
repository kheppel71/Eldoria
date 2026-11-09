"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from commands.interaction_cmds import (
    CmdTalk, CmdDrink, CmdRead, CmdLight, CmdCatch,
    CmdTurn, CmdMine, CmdCleanse, CmdInsert,
    CmdFish, CmdReel, CmdCook, CmdMapper
)
from commands.nightmare_cmds import (
    CmdScore, CmdLimbs, CmdEquipment, CmdWield, CmdWear, CmdRemove,
    CmdGuilds, CmdJoinGuild, CmdSkills, CmdTrain,
    CmdResurrect, CmdLootCorpse,
    CmdBalance, CmdDeposit, CmdWithdraw, CmdVault,
    CmdKill, CmdBash, CmdBackstab, CmdCast, CmdFlee, CmdDisengage, CmdRest,
    CmdRace, CmdSpellbook, CmdStudy, CmdSubclass, CmdAbility, CmdRacial,
    CmdHp, CmdWimpy, CmdConsider, CmdKick, CmdDisarm, CmdParty, CmdPartySay,
    CmdAssist, CmdSpells, CmdSearch, CmdListen, CmdSmell, CmdAppraise,
    CmdWhoNightmare
)
from commands.language_cmds import (
    CmdLanguages, CmdSpeak, CmdSayLang, CmdWhisperLang, CmdStudyLang
)
from commands.sailing_cmds import (
    CmdFerries, CmdFare, CmdBoard, CmdCoffers
)
from commands.importer_cmds import CmdImportZone
from commands.map_cmds import CmdMap
from commands.justice_cmds import (
    CmdBounties, CmdBounty, CmdSurrender, CmdBail, CmdServeTime, CmdCriminalRecord
)
from commands.quest_cmds import (
    CmdQuests, CmdQuestInfo, CmdQuestStart
)
from commands.durability_cmds import (
    CmdCondition, CmdRepair, CmdSharpen
)
from commands.harvest_cmds import (
    CmdSkin, CmdForage, CmdEnvenom
)
from commands.weather_cmds import (
    CmdTime, CmdWeather, CmdSetWeather
)
from commands.board_mail_cmds import (
    CmdBulletinBoard, CmdMail, CmdMailbox
)
from commands.mount_cmds import (
    CmdMount, CmdDismount, CmdCharge, CmdSaddlebags
)
from commands.thievery_cmds import (
    CmdPeek, CmdSteal, CmdFence
)
from commands.housing_cmds import (
    CmdLock, CmdUnlock, CmdPickLock, CmdKeyring, CmdBuyHouse
)
from commands.crafting_cmds import (
    CmdBrew, CmdCookFood, CmdEat
)
from commands.economy_cmds import (
    CmdPeddler
)
from commands.necromancy_cmds import (
    CmdTurnUndead, CmdAnimateDead, CmdOrderThrall
)
from commands.territory_cmds import (
    CmdTerritories, CmdClaimTerritory
)
from commands.finger_immortal_cmds import (
    CmdFinger, CmdPlan, CmdInvis, CmdGoto, CmdTrans, CmdDestruct
)
from commands.fishing_cmds import (
    CmdBaitHook, CmdCastLine, CmdReelLine
)
from commands.trap_cmds import (
    CmdSetTrap, CmdCaltrops
)
from commands.arena_cmds import (
    CmdDuel, CmdSpectate
)
from commands.bard_cmds import (
    CmdPlayInstrument, CmdSingSong
)
from commands.trophy_cmds import (
    CmdTaxidermy, CmdMountTrophy, CmdTrophies
)
from commands.marriage_cmds import (
    CmdPropose, CmdAcceptProposal, CmdDivorce, CmdWeddingRing
)
from commands.intoxication_cmds import (
    CmdOrderDrink, CmdIntoxication, CmdSober
)
from commands.deity_cmds import (
    CmdDeities, CmdWorship, CmdPray, CmdSacrifice
)
from commands.enchanting_cmds import (
    CmdInscribe, CmdSocket
)
from commands.disguise_cmds import (
    CmdDisguise, CmdUnmask, CmdScrutinize
)
from commands.dungeon_secret_cmds import (
    CmdSearchWall, CmdDisarmTrap, CmdPushBrick
)
from commands.identification_cmds import (
    CmdIdentify, CmdLore
)
from commands.curse_cmds import (
    CmdUncurse
)
from commands.camping_cmds import (
    CmdPitchTent, CmdLightCampfire, CmdStrikeCamp
)
from commands.taming_cmds import (
    CmdTame, CmdPet, CmdFeedPet
)
from commands.gambling_cmds import (
    CmdRollDice
)
from commands.specialization_cmds import (
    CmdSpecialize
)
from commands.social_cmds import (
    CmdFeelings, CmdSocialAction
)
from commands.mining_cmds import (
    CmdProspect, CmdMineOre, CmdSmelt
)
from commands.scribing_cmds import (
    CmdScribeScroll, CmdReadScroll
)
from commands.cartography_cmds import (
    CmdDrawMap, CmdLandmark, CmdViewMap
)
from commands.mentoring_cmds import (
    CmdGuide, CmdNewbie, CmdTutor
)
from commands.reincarnation_cmds import (
    CmdReincarnate, CmdSoulShards
)
from commands.title_cmds import (
    CmdTitles, CmdSetTitle
)
from commands.scabbard_cmds import (
    CmdSheathe, CmdDraw
)
from commands.raid_cmds import (
    CmdEvents
)
from commands.gravedigging_cmds import (
    CmdDig
)
from commands.beekeeping_cmds import (
    CmdSmokeBees, CmdHarvestHive, CmdBrewMead, CmdCraftCandle
)
from commands.leaderboard_cmds import (
    CmdLeaderboards
)
from commands.astrology_cmds import (
    CmdStars
)
from commands.herbalism_cmds import (
    CmdForage, CmdCraftPoultice, CmdApplyPoultice, CmdCraftPoison, CmdCoatWeapon
)
from commands.exorcism_cmds import (
    CmdCurseInfo, CmdExorcise
)
from commands.hireling_cmds import (
    CmdHirelings, CmdHire, CmdOrderHireling, CmdDismissHireling
)
from commands.caravan_cmds import (
    CmdCaravans, CmdEscortCaravan, CmdDefendWagon
)
from commands.library_cmds import (
    CmdReadTome, CmdTranscribe, CmdLore
)
from commands.shipwright_cmds import (
    CmdBuildShip, CmdBoardShip, CmdSail, CmdAnchorShip
)
from commands.ward_cmds import (
    CmdCarveRune, CmdDisarmGlyph
)
from commands.survival_camp_cmds import (
    CmdPitchTent, CmdStrikeTent, CmdKindleFire, CmdRestCamp
)
from commands.busking_cmds import (
    CmdBeg, CmdBusk
)
from commands.fossil_cmds import (
    CmdCleanSpecimen, CmdDonateMuseum, CmdMuseum
)
from commands.tarot_cmds import (
    CmdDrawCard, CmdTarotRead
)
from commands.falconry_cmds import (
    CmdCallHawk, CmdSendHawk, CmdFeedHawk
)
from commands.glassblowing_cmds import (
    CmdGatherQuartz, CmdBlowGlass
)
from commands.truffle_cmds import (
    CmdLeashHound, CmdTruffleHunt, CmdDigTruffle, CmdCookFeast
)
from commands.blackmarket_cmds import (
    CmdWhisperPass, CmdBlackMarket, CmdSmuggleBuy
)
from commands.tinkering_cmds import (
    CmdTinker, CmdWindGadget, CmdDeployDecoy
)
from commands.bathhouse_cmds import (
    CmdBathhouse, CmdSoak, CmdWashGrime
)
from commands.siege_cmds import (
    CmdRamGate, CmdRepairGate, CmdGateStatus
)
from commands.horse_taming_cmds import (
    CmdLasso, CmdBreakHorse, CmdBreedMounts, CmdStableInfo
)
from commands.leatherworking_cmds import (
    CmdSkinHide, CmdTanLeather, CmdCraftArmor
)
from commands.carnival_cmds import (
    CmdCarnival, CmdTestStrength, CmdPlayTarget
)
from commands.apothecary_leeching_cmds import (
    CmdHumors, CmdJarLeeches, CmdApplyLeeches, CmdBloodlet
)
from commands.lapidary_cmds import (
    CmdFacetGem, CmdCraftJewelry
)
from commands.illusion_cmds import (
    CmdMirrorImage, CmdPhantasm, CmdDispelIllusion
)
from commands.spelunking_cmds import (
    CmdTieRope, CmdRappel, CmdAnchorBridge
)
from commands.cheesemaking_cmds import (
    CmdMilkLivestock, CmdChurnButter, CmdPressCheese, CmdAgeCheese
)
from commands.toll_cmds import (
    CmdPayToll, CmdCustomsInspect
)
from commands.chalk_cmds import (
    CmdChalkMark, CmdReadMarks, CmdClearChalk
)
from commands.confession_cmds import (
    CmdConfess, CmdPerformPenance, CmdAbsolve
)
from commands.diving_cmds import (
    CmdDivingSuit, CmdDive, CmdSalvageDepths, CmdPryChest
)
from commands.venom_cmds import (
    CmdMilkVenom, CmdBrewAntidote, CmdApplyAntidote
)
from commands.pigeon_cmds import (
    CmdPigeonLoft, CmdSendPigeon, CmdReadLetter
)
from commands.woodcarving_cmds import (
    CmdWhittle, CmdCarveFlute, CmdCarveLute
)
from commands.banner_cmds import (
    CmdPlantBanner, CmdUprootBanner, CmdBlowWarhorn
)
from commands.seance_cmds import (
    CmdSeance, CmdSummonSpirit, CmdQuestionGhost
)


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdTalk)
        self.add(CmdDrink)
        self.add(CmdRead)
        self.add(CmdLight)
        self.add(CmdCatch)
        self.add(CmdTurn)
        self.add(CmdMine)
        self.add(CmdCleanse)
        self.add(CmdInsert)
        self.add(CmdFish)
        self.add(CmdReel)
        self.add(CmdCook)
        self.add(CmdMapper)

        # Nightmare LPmud Commands
        self.add(CmdScore)
        self.add(CmdLimbs)
        self.add(CmdEquipment)
        self.add(CmdWield)
        self.add(CmdWear)
        self.add(CmdRemove)
        self.add(CmdGuilds)
        self.add(CmdJoinGuild)
        self.add(CmdSkills)
        self.add(CmdTrain)
        self.add(CmdResurrect)
        self.add(CmdLootCorpse)
        self.add(CmdBalance)
        self.add(CmdDeposit)
        self.add(CmdWithdraw)
        self.add(CmdVault)
        self.add(CmdKill)
        self.add(CmdBash)
        self.add(CmdBackstab)
        self.add(CmdCast)
        self.add(CmdFlee)
        self.add(CmdDisengage)
        self.add(CmdRest)
        self.add(CmdRace)
        self.add(CmdSpellbook)
        self.add(CmdStudy)
        self.add(CmdSubclass)
        self.add(CmdAbility)
        self.add(CmdRacial)
        self.add(CmdHp)
        self.add(CmdWimpy)
        self.add(CmdConsider)
        self.add(CmdKick)
        self.add(CmdDisarm)
        self.add(CmdParty)
        self.add(CmdPartySay)
        self.add(CmdAssist)
        self.add(CmdSpells)
        self.add(CmdSearch)
        self.add(CmdListen)
        self.add(CmdSmell)
        self.add(CmdAppraise)
        self.add(CmdWhoNightmare)

        # Nightmare LPmud Language System
        self.add(CmdLanguages)
        self.add(CmdSpeak)
        self.add(CmdSayLang)
        self.add(CmdWhisperLang)
        self.add(CmdStudyLang)

        # Maritime Sailing, Ferries & Coffers
        self.add(CmdFerries)
        self.add(CmdFare)
        self.add(CmdBoard)
        self.add(CmdCoffers)

        # World Importers
        self.add(CmdImportZone)

        # In-Game Mini-Map & Automap
        self.add(CmdMap)

        # Nightmare LPmud Justice & Bounty System
        self.add(CmdBounties)
        self.add(CmdBounty)
        self.add(CmdSurrender)
        self.add(CmdBail)
        self.add(CmdServeTime)
        self.add(CmdCriminalRecord)

        # Nightmare LPmud Quest Engine & Progression
        self.add(CmdQuests)
        self.add(CmdQuestInfo)
        self.add(CmdQuestStart)

        # Nightmare LPmud Equipment Durability & Blacksmithing
        self.add(CmdCondition)
        self.add(CmdRepair)
        self.add(CmdSharpen)

        # Nightmare LPmud Wilderness Harvest, Skinning & Envenoming
        self.add(CmdSkin)
        self.add(CmdForage)
        self.add(CmdEnvenom)

        # Nightmare LPmud Celestial Cycle & Weather
        self.add(CmdTime)
        self.add(CmdWeather)
        self.add(CmdSetWeather)

        # Nightmare LPmud Bulletin Boards & Courier Postal System
        self.add(CmdBulletinBoard)
        self.add(CmdMail)
        self.add(CmdMailbox)

        # Nightmare LPmud Mounts & Cavalry
        self.add(CmdMount)
        self.add(CmdDismount)
        self.add(CmdCharge)
        self.add(CmdSaddlebags)

        # Nightmare LPmud Rogue Thievery & Shoplifting
        self.add(CmdPeek)
        self.add(CmdSteal)
        self.add(CmdFence)

        # Nightmare LPmud Housing, Keys & Lockpicking
        self.add(CmdLock)
        self.add(CmdUnlock)
        self.add(CmdPickLock)
        self.add(CmdKeyring)
        self.add(CmdBuyHouse)

        # Nightmare LPmud Alchemy & Cooking
        self.add(CmdBrew)
        self.add(CmdCookFood)
        self.add(CmdEat)

        # Nightmare LPmud Merchant Peddlers
        self.add(CmdPeddler)

        # Nightmare LPmud Holy Turning & Necromancy
        self.add(CmdTurnUndead)
        self.add(CmdAnimateDead)
        self.add(CmdOrderThrall)

        # Nightmare LPmud Guild Territory Control
        self.add(CmdTerritories)
        self.add(CmdClaimTerritory)

        # Nightmare LPmud Finger, Plan & Immortal Suite
        self.add(CmdFinger)
        self.add(CmdPlan)
        self.add(CmdInvis)
        self.add(CmdGoto)
        self.add(CmdTrans)
        self.add(CmdDestruct)

        # Nightmare LPmud Wilderness Fishing & Angling
        self.add(CmdBaitHook)
        self.add(CmdCastLine)
        self.add(CmdReelLine)

        # Nightmare LPmud Hunting Traps & Caltrops
        self.add(CmdSetTrap)
        self.add(CmdCaltrops)

        # Nightmare LPmud Grand Arena Duels & Spectating
        self.add(CmdDuel)
        self.add(CmdSpectate)

        # Nightmare LPmud Bardic Songs & Instruments
        self.add(CmdPlayInstrument)
        self.add(CmdSingSong)

        # Nightmare LPmud Trophy Taxidermy & Room Mounts
        self.add(CmdTaxidermy)
        self.add(CmdMountTrophy)
        self.add(CmdTrophies)

        # Nightmare LPmud Marriage & Spousal Ring
        self.add(CmdPropose)
        self.add(CmdAcceptProposal)
        self.add(CmdDivorce)
        self.add(CmdWeddingRing)

        # Nightmare LPmud Tavern Intoxication & Drunkenness
        self.add(CmdOrderDrink)
        self.add(CmdIntoxication)
        self.add(CmdSober)

        # Nightmare LPmud Deities, Shrines & Sacrifices
        self.add(CmdDeities)
        self.add(CmdWorship)
        self.add(CmdPray)
        self.add(CmdSacrifice)

        # Nightmare LPmud Rune Inscription & Gem Socketing
        self.add(CmdInscribe)
        self.add(CmdSocket)

        # Nightmare LPmud Rogue Disguises & False Identities
        self.add(CmdDisguise)
        self.add(CmdUnmask)
        self.add(CmdScrutinize)

        # Nightmare LPmud Dungeon Hazards & Secret Passages
        self.add(CmdSearchWall)
        self.add(CmdDisarmTrap)
        self.add(CmdPushBrick)

        # Nightmare LPmud Artifact Identification & Lore
        self.add(CmdIdentify)
        self.add(CmdLore)

        # Nightmare LPmud Cursed Items & Purification
        self.add(CmdUncurse)

        # Nightmare LPmud Wilderness Camping & Shelters
        self.add(CmdPitchTent)
        self.add(CmdLightCampfire)
        self.add(CmdStrikeCamp)

        # Nightmare LPmud Beast Taming & Companions
        self.add(CmdTame)
        self.add(CmdPet)
        self.add(CmdFeedPet)

        # Nightmare LPmud Tavern Dice Gambling
        self.add(CmdRollDice)

        # Nightmare LPmud Master Specializations
        self.add(CmdSpecialize)

        # Nightmare LPmud Socials & Feelings Soul Engine
        self.add(CmdFeelings)
        self.add(CmdSocialAction)

        # Nightmare LPmud Mining, Prospecting & Smelting
        self.add(CmdProspect)
        self.add(CmdMineOre)
        self.add(CmdSmelt)

        # Nightmare LPmud Spell Scribing & Magic Scrolls
        self.add(CmdScribeScroll)
        self.add(CmdReadScroll)

        # Nightmare LPmud Wilderness Cartography & Mapping
        self.add(CmdDrawMap)
        self.add(CmdLandmark)
        self.add(CmdViewMap)

        # Nightmare LPmud Player Mentoring & Novice Channel
        self.add(CmdGuide)
        self.add(CmdNewbie)
        self.add(CmdTutor)

        # Nightmare LPmud Soul Shards & Reincarnation
        self.add(CmdReincarnate)
        self.add(CmdSoulShards)

        # Nightmare LPmud Renown Titles, Epithets & Heroic Accolades
        self.add(CmdTitles)
        self.add(CmdSetTitle)

        # Nightmare LPmud Weapon Scabbards & Quick-Draw Tactical Sheathing
        self.add(CmdSheathe)
        self.add(CmdDraw)

        # Nightmare LPmud Dynamic World Boss Raids & Town Invasions
        self.add(CmdEvents)

        # Nightmare LPmud Gravedigging, Crypt Excavation & Relic Hunting
        self.add(CmdDig)

        # Nightmare LPmud Wild Beekeeping, Honeycombs & Mead Fermentation
        self.add(CmdSmokeBees)
        self.add(CmdHarvestHive)
        self.add(CmdBrewMead)
        self.add(CmdCraftCandle)

        # Nightmare LPmud Hall of Champions & Realm Leaderboards
        self.add(CmdLeaderboards)

        # Nightmare LPmud Astrological Constellations & Zodiac Alignments
        self.add(CmdStars)

        # Nightmare LPmud Wilderness Herbalism, Poultices & Blade Poisons
        self.add(CmdForage)
        self.add(CmdCraftPoultice)
        self.add(CmdApplyPoultice)
        self.add(CmdCraftPoison)
        self.add(CmdCoatWeapon)

        # Nightmare LPmud Cursed Relics, Haunted Idols & Exorcism Rites
        self.add(CmdCurseInfo)
        self.add(CmdExorcise)

        # Nightmare LPmud Mercenary Hirelings & Traveling Companions
        self.add(CmdHirelings)
        self.add(CmdHire)
        self.add(CmdOrderHireling)
        self.add(CmdDismissHireling)

        # Nightmare LPmud Merchant Caravans & Highwayman Ambushes
        self.add(CmdCaravans)
        self.add(CmdEscortCaravan)
        self.add(CmdDefendWagon)

        # Nightmare LPmud Grand Library Archives, Lore Tomes & Archaeological Research
        self.add(CmdReadTome)
        self.add(CmdTranscribe)
        self.add(CmdLore)

        # Nightmare LPmud Shipwright Naval Crafting, Dinghies & Voyages
        self.add(CmdBuildShip)
        self.add(CmdBoardShip)
        self.add(CmdSail)
        self.add(CmdAnchorShip)

        # Nightmare LPmud Runecarving, Protective Wards & Explosive Sigils
        self.add(CmdCarveRune)
        self.add(CmdDisarmGlyph)

        # Nightmare LPmud Wilderness Survival Camps, Canvas Tents & Hearth
        self.add(CmdPitchTent)
        self.add(CmdStrikeTent)
        self.add(CmdKindleFire)
        self.add(CmdRestCamp)

        # Nightmare LPmud Street Urchin Begging, Busking & Performances
        self.add(CmdBeg)
        self.add(CmdBusk)

        # Nightmare LPmud Paleontological Fossils, Bone Restoration & Museum
        self.add(CmdCleanSpecimen)
        self.add(CmdDonateMuseum)
        self.add(CmdMuseum)

        # Nightmare LPmud Eldritch Tarot Divination & Fate Cards
        self.add(CmdDrawCard)
        self.add(CmdTarotRead)

        # Nightmare LPmud Falconry, Hunting Birds & Aerial Reconnaissance
        self.add(CmdCallHawk)
        self.add(CmdSendHawk)
        self.add(CmdFeedHawk)

        # Nightmare LPmud Glassblowing, Alchemical Phials & Stained Glass
        self.add(CmdGatherQuartz)
        self.add(CmdBlowGlass)

        # Nightmare LPmud Truffle Hunting, Sniffer Hounds & Culinary Feasts
        self.add(CmdLeashHound)
        self.add(CmdTruffleHunt)
        self.add(CmdDigTruffle)
        self.add(CmdCookFeast)

        # Nightmare LPmud Underworld Black Market & Smuggler Dens
        self.add(CmdWhisperPass)
        self.add(CmdBlackMarket)
        self.add(CmdSmuggleBuy)

        # Nightmare LPmud Clockwork Tinkering, Automatons & Decoys
        self.add(CmdTinker)
        self.add(CmdWindGadget)
        self.add(CmdDeployDecoy)

        # Nightmare LPmud Thermal Bathhouse, Steam Vapor & Mineral Soaking
        self.add(CmdBathhouse)
        self.add(CmdSoak)
        self.add(CmdWashGrime)

        # Nightmare LPmud Siege Warfare, Battering Rams & Gate Breaching
        self.add(CmdRamGate)
        self.add(CmdRepairGate)
        self.add(CmdGateStatus)

        # Nightmare LPmud Wild Horse Taming, Mustang Breaking & Breeding
        self.add(CmdLasso)
        self.add(CmdBreakHorse)
        self.add(CmdBreedMounts)
        self.add(CmdStableInfo)

        # Nightmare LPmud Leatherworking, Tanning Vats & Armor Crafting
        self.add(CmdSkinHide)
        self.add(CmdTanLeather)
        self.add(CmdCraftArmor)

        # Nightmare LPmud Traveling Carnival of Oddities & Games of Skill
        self.add(CmdCarnival)
        self.add(CmdTestStrength)
        self.add(CmdPlayTarget)

        # Nightmare LPmud Barber-Surgeon Leeching, Bloodletting & Humors
        self.add(CmdHumors)
        self.add(CmdJarLeeches)
        self.add(CmdApplyLeeches)
        self.add(CmdBloodlet)

        # Nightmare LPmud Lapidary Gemcutting, Faceting & Jeweled Filigree
        self.add(CmdFacetGem)
        self.add(CmdCraftJewelry)

        # Nightmare LPmud Illusionism, Mirror Images & Phantasms
        self.add(CmdMirrorImage)
        self.add(CmdPhantasm)
        self.add(CmdDispelIllusion)

        # Nightmare LPmud Wilderness Spelunking & Rappelling
        self.add(CmdTieRope)
        self.add(CmdRappel)
        self.add(CmdAnchorBridge)

        # Nightmare LPmud Artisan Cheesemaking & Cellar Aging
        self.add(CmdMilkLivestock)
        self.add(CmdChurnButter)
        self.add(CmdPressCheese)
        self.add(CmdAgeCheese)

        # Nightmare LPmud Toll Bridges & Customs Inspections
        self.add(CmdPayToll)
        self.add(CmdCustomsInspect)

        # Nightmare LPmud Dungeon Chalk Markings & Wayfinding
        self.add(CmdChalkMark)
        self.add(CmdReadMarks)
        self.add(CmdClearChalk)

        # Nightmare LPmud Cathedral Confessionals, Penance & Absolution
        self.add(CmdConfess)
        self.add(CmdPerformPenance)
        self.add(CmdAbsolve)

        # Nightmare LPmud Underwater Diving, Shipwreck Salvage & Doubloons
        self.add(CmdDivingSuit)
        self.add(CmdDive)
        self.add(CmdSalvageDepths)
        self.add(CmdPryChest)

        # Nightmare LPmud Venom Milking, Toxic Brewing & Universal Antidotes
        self.add(CmdMilkVenom)
        self.add(CmdBrewAntidote)
        self.add(CmdApplyAntidote)

        # Nightmare LPmud Aviary Courier Pigeons, Message Canisters & Skymail
        self.add(CmdPigeonLoft)
        self.add(CmdSendPigeon)
        self.add(CmdReadLetter)

        # Nightmare LPmud Artisan Woodcarving, Whittling & Musical Instruments
        self.add(CmdWhittle)
        self.add(CmdCarveFlute)
        self.add(CmdCarveLute)

        # Nightmare LPmud Guild War Banners, Standards & Rallying Warhorns
        self.add(CmdPlantBanner)
        self.add(CmdUprootBanner)
        self.add(CmdBlowWarhorn)

        # Nightmare LPmud Graveyard Séances, Spirit Mediums & Talking Boards
        self.add(CmdSeance)
        self.add(CmdSummonSpirit)
        self.add(CmdQuestionGhost)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
