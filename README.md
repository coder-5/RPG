# RPG Adventure Game

A text-based role-playing game featuring character progression, turn-based combat, quests, and exploration.

## Features

- **Three Character Classes**: Warrior, Mage, and Rogue, each with unique stats and special abilities
- **Turn-Based Combat**: Strategic battles against various enemies
- **Character Progression**: Level up system with stat increases
- **Quest System**: Complete quests for rewards and experience
- **Exploration**: Multiple locations to discover, each with different danger levels
- **Inventory System**: Collect items, weapons, armor, and potions
- **Shop System**: Buy and sell items at the village shop
- **Save/Load System**: Save your progress and continue later

## Requirements

- Python 3.6 or higher

## Installation

1. Clone or download this repository
2. Navigate to the game directory
3. Run the game:

```bash
python3 game.py
```

or make it executable:

```bash
chmod +x game.py
./game.py
```

## How to Play

### Character Creation

When starting a new game, you'll create your character by:
1. Choosing a name
2. Selecting a class:
   - **Warrior**: High HP and strength, specializes in physical attacks
   - **Mage**: High MP and intelligence, powerful magic attacks
   - **Rogue**: High agility, critical hits and evasion

### Game Controls

The game is menu-driven. Simply enter the number corresponding to your choice.

### Main Actions

1. **View Stats**: Check your character's current stats, equipment, and progress
2. **Inventory**: Manage your items, equip weapons and armor, use potions
3. **Explore**: Search for random encounters and battles
4. **Travel**: Move between different locations
5. **Visit Shop**: Buy and sell items (available in Riverside Village)
6. **Quests**: View, accept, and track quests
7. **Rest**: Restore HP and MP to maximum
8. **Save Game**: Save your progress
9. **Main Menu**: Return to the main menu

### Combat

Combat is turn-based. During your turn, you can:
- **Attack**: Basic physical attack
- **Special Ability**: Class-specific powerful attack (costs MP)
  - Warrior: Power Strike (2x damage)
  - Mage: Fireball (magic damage based on intelligence)
  - Rogue: Backstab (critical hit)
- **Use Item**: Use a potion from your inventory
- **Run**: Attempt to escape from battle

### Locations

- **Riverside Village**: Safe starting area with a shop
- **Dark Forest**: Moderately dangerous forest area
- **Ancient Cave**: Mysterious cave with treasures
- **Abandoned Ruins**: Dangerous ruins haunted by undead
- **Misty Mountains**: Treacherous mountain peaks

### Quests

Accept and complete quests to earn gold, experience, and special items:
- **The Goblin Menace**: Defeat enemies to protect the village
- **Cave Explorer**: Discover the secrets of the Ancient Cave
- **Mountain Climber**: Reach the peak of the Misty Mountains

### Progression

- Defeat enemies to gain experience and gold
- Level up to increase your stats
- Collect better weapons and armor
- Complete quests for rewards
- Explore dangerous areas for greater challenges

### Tips

- Rest frequently to keep your HP and MP at maximum
- Buy potions before exploring dangerous areas
- Equip better weapons and armor as you find them
- Accept quests early to complete them as you explore
- Higher danger level areas have stronger enemies but better rewards
- Save your game regularly!

## Game Files

- `game.py`: Main game file and entry point
- `character.py`: Character, player, enemy, and item classes
- `combat.py`: Combat system and battle mechanics
- `world.py`: Game world, locations, shops, and quests
- `save_system.py`: Save and load game functionality

## Save Files

Save files are stored in the `saves/` directory and are named after your character (e.g., `hero_save.json`).

## Credits

Created as a classic text-based RPG adventure game.

## License

Free to use and modify.

---

Enjoy your adventure!
