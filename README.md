# Eldoria MUD

**Eldoria** is an immersive, high-fantasy text-based virtual world powered by the [Evennia](https://www.evennia.com/) Python MUD engine. It faithfully implements and modernizes the deep, authentic mechanics of classic **Nightmare LPmud**, featuring layered combat, crafting, survival, exploration, economy, and guild politics.

---

## 🌟 Key Features & Systems

### 1. Core Combat, Limbs & Death
- **Hit Locations & Limb Severing**: Head, torso, arms, hands, legs, and feet tracking independent health, armor, and crippling conditions.
- **Ghosts & Resurrection**: Death transitions players to spiritual ghosts who must seek high clerics or sacred altars for bodily revival.
- **Weapon Durability & Repair**: Weapons and armor wear down through use and require blacksmithing repair.
- **Tactical Quick-Draw & Sheathing**: Belt and back scabbards with instant draw readiness.

### 2. Classes, Guilds & Prestige Specializations
- **Guild Progression**: Fighters, Mages, Clerics, Rogues, Monks, and Necromancers with unique spellbooks, chants, and training halls.
- **Prestige Subclasses**: Paladin, Berserker, Archmage, Pyromancer, Shadowstalker, Assassin, and Druid.
- **Guild Territory Control**: Capture points and nodes across the realm contested between rival guilds.

### 3. Magic, Deities & Spirituality
- **Chants & Reagents**: Verbal chants, sulfur/ginseng reagents, and scroll scribing.
- **Divine Pantheons & Shrines**: Aligning with deities for favor, prayers, and divine intervention.
- **Cathedral Confessionals & Absolution**: Confessing sins and performing penance for blessings.
- **Illusionism & Wards**: Mirror images, phantasmal terrors, and etched explosive floor sigils.

### 4. Wilderness Survival & Exploration
- **Celestial Clock & Dynamic Weather**: 24-hour lunar cycles (blood moon, new moon) and elemental storm fronts.
- **Survival Camping**: Pitching canvas expedition tents and kindling stone campfires.
- **Spelunking & Mountaineering**: Silk rappelling ropes, vertical descents, and chasm traverse bridges.
- **Falconry & Hunting Birds**: Falcons, harriers, and owls for aerial scouting and game hunting.
- **Wild Horse Taming**: Rawhide lassoing, bucking breaking checks, and equestrian stud breeding.
- **Underwater Diving**: Weighted brass diving helmets and salvage prying in sunken galleons.

### 5. Economy, Trade & Crafting
- **Banking & Vaults**: Secure coin deposits and personal bank vaults.
- **Caravans & Escorts**: Defending merchant wagon trains from roadside bandit ambushes.
- **Underworld Black Markets**: Secret shadow passphrases and contraband bazaar fencing.
- **Artisan Crafts**:
  - Mineral prospecting, mining, and forge smelting.
  - Alchemy cauldrons, herbal poultices, and lethal poison distillation.
  - Lapidary gemcutting and filigree jewelry crafting.
  - Leather tanning vats and armor tailoring.
  - Blowpipe glassblowing for reinforced alchemical phials.
  - Whittling acoustic pine flutes and spruce bardic lutes.
  - Dairy butter churning, cheese pressing, and cellar maturation.

### 6. Roleplay, Lore & Accolades
- **Hall of Champions**: Realm leaderboards tracking Gladiators, Questors, Tycoons, and Slayers.
- **Renown Titles & Accolades**: Unlocked honorific prefixes and heroic epithets.
- **Grand Library Archives**: Deciphering ancient codices for permanent lore knowledge.
- **Eldritch Tarot Divination**: 22-card Major Arcana fate draws and 3-card past/present/future spreads.
- **Courier Pigeon Skymail**: Airborne letter cylinders delivered directly between remote adventurers.

---

## 🚀 Running the Server

1. **Activate Virtual Environment**:
   ```powershell
   evennia-env\Scripts\activate
   ```

2. **Run Server**:
   ```powershell
   cd mygame
   evennia start
   ```

3. **Reload Server In-Game or via CLI**:
   ```powershell
   evennia reload
   ```

4. **Connect**:
   - Telnet: `localhost:4000`
   - Web Client: `http://localhost:4001`
