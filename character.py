"""
Character module for the RPG game
Defines player and enemy characters with stats, abilities, and inventory
"""

import random
from typing import Dict, List, Optional


class Item:
    """Represents an item in the game"""
    def __init__(self, name: str, item_type: str, value: int, description: str = ""):
        self.name = name
        self.item_type = item_type  # weapon, armor, potion, quest
        self.value = value  # damage/defense/healing/gold value
        self.description = description

    def __str__(self):
        return f"{self.name} ({self.item_type}) - {self.description}"


class Character:
    """Base character class for players and enemies"""
    def __init__(self, name: str, char_class: str = "Adventurer"):
        self.name = name
        self.char_class = char_class
        self.level = 1
        self.experience = 0
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.strength = 10
        self.intelligence = 10
        self.agility = 10
        self.defense = 5
        self.gold = 50
        self.inventory: List[Item] = []
        self.equipped_weapon: Optional[Item] = None
        self.equipped_armor: Optional[Item] = None

    def take_damage(self, damage: int) -> int:
        """Apply damage to character, returns actual damage taken"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage

    def heal(self, amount: int):
        """Heal character"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hp > 0

    def attack(self) -> int:
        """Calculate attack damage"""
        base_damage = self.strength
        weapon_damage = self.equipped_weapon.value if self.equipped_weapon else 0
        variance = random.randint(-2, 5)
        return max(1, base_damage + weapon_damage + variance)

    def add_experience(self, exp: int):
        """Add experience and check for level up"""
        self.experience += exp
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level_up()

    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.max_mp += 10
        self.mp = self.max_mp
        self.strength += 3
        self.intelligence += 3
        self.agility += 2
        self.defense += 2

    def add_item(self, item: Item):
        """Add item to inventory"""
        self.inventory.append(item)

    def remove_item(self, item: Item):
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)

    def equip_weapon(self, item: Item) -> bool:
        """Equip a weapon"""
        if item.item_type == "weapon":
            if self.equipped_weapon:
                self.inventory.append(self.equipped_weapon)
            self.equipped_weapon = item
            if item in self.inventory:
                self.inventory.remove(item)
            return True
        return False

    def equip_armor(self, item: Item) -> bool:
        """Equip armor"""
        if item.item_type == "armor":
            if self.equipped_armor:
                self.inventory.append(self.equipped_armor)
            self.equipped_armor = item
            self.defense += item.value
            if item in self.inventory:
                self.inventory.remove(item)
            return True
        return False

    def get_stats(self) -> str:
        """Get character stats as string"""
        stats = f"\n{'='*50}\n"
        stats += f"{self.name} - Level {self.level} {self.char_class}\n"
        stats += f"{'='*50}\n"
        stats += f"HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp}\n"
        stats += f"Experience: {self.experience}/{self.level * 100}\n"
        stats += f"Strength: {self.strength} | Intelligence: {self.intelligence}\n"
        stats += f"Agility: {self.agility} | Defense: {self.defense}\n"
        stats += f"Gold: {self.gold}\n"
        if self.equipped_weapon:
            stats += f"Weapon: {self.equipped_weapon.name} (+{self.equipped_weapon.value} damage)\n"
        if self.equipped_armor:
            stats += f"Armor: {self.equipped_armor.name} (+{self.equipped_armor.value} defense)\n"
        stats += f"{'='*50}\n"
        return stats


class Player(Character):
    """Player character with special abilities"""
    def __init__(self, name: str, char_class: str):
        super().__init__(name, char_class)
        self.setup_class()

    def setup_class(self):
        """Setup initial stats based on character class"""
        if self.char_class == "Warrior":
            self.strength = 15
            self.max_hp = 120
            self.hp = 120
            self.defense = 8
            self.equipped_weapon = Item("Iron Sword", "weapon", 10, "A sturdy iron blade")
        elif self.char_class == "Mage":
            self.intelligence = 18
            self.max_mp = 80
            self.mp = 80
            self.strength = 6
            self.equipped_weapon = Item("Wooden Staff", "weapon", 5, "A magical staff")
        elif self.char_class == "Rogue":
            self.agility = 18
            self.strength = 12
            self.max_hp = 90
            self.hp = 90
            self.equipped_weapon = Item("Dagger", "weapon", 8, "A sharp dagger")

    def special_ability(self, target: Character) -> tuple[int, str]:
        """Use class-specific special ability"""
        if self.char_class == "Warrior":
            if self.mp >= 15:
                self.mp -= 15
                damage = int(self.attack() * 2)
                return damage, f"{self.name} uses Power Strike!"
            else:
                return 0, "Not enough MP for Power Strike!"

        elif self.char_class == "Mage":
            if self.mp >= 20:
                self.mp -= 20
                damage = self.intelligence * 3 + random.randint(5, 15)
                return damage, f"{self.name} casts Fireball!"
            else:
                return 0, "Not enough MP for Fireball!"

        elif self.char_class == "Rogue":
            if self.mp >= 12:
                self.mp -= 12
                # Critical hit chance
                damage = int(self.attack() * (1.5 + random.random()))
                return damage, f"{self.name} performs a Backstab!"
            else:
                return 0, "Not enough MP for Backstab!"

        return 0, "No special ability available"


class Enemy(Character):
    """Enemy character"""
    def __init__(self, name: str, level: int = 1):
        super().__init__(name, "Enemy")
        self.level = level
        self.adjust_for_level()

    def adjust_for_level(self):
        """Adjust stats based on enemy level"""
        for _ in range(self.level - 1):
            self.max_hp += 15
            self.strength += 2
            self.defense += 1
            self.agility += 1
        self.hp = self.max_hp

    def get_reward(self) -> tuple[int, int]:
        """Get gold and experience rewards"""
        gold = self.level * random.randint(10, 30)
        exp = self.level * random.randint(20, 40)
        return gold, exp
