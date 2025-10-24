"""
Combat module for the RPG game
Handles turn-based combat between player and enemies
"""

import random
import time
from character import Player, Enemy, Item


class Combat:
    """Handles combat encounters"""
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 1

    def display_combat_status(self):
        """Display combat status"""
        print(f"\n{'='*60}")
        print(f"TURN {self.turn}")
        print(f"{'='*60}")
        print(f"{self.player.name}: HP {self.player.hp}/{self.player.max_hp} | MP {self.player.mp}/{self.player.max_mp}")
        print(f"{self.enemy.name}: HP {self.enemy.hp}/{self.enemy.max_hp}")
        print(f"{'='*60}\n")

    def player_turn(self) -> bool:
        """Handle player's turn. Returns True if combat should continue"""
        while True:
            print("\nYour turn! Choose an action:")
            print("1. Attack")
            print("2. Special Ability")
            print("3. Use Item")
            print("4. Run")

            choice = input("\nEnter choice (1-4): ").strip()

            if choice == "1":
                damage = self.player.attack()
                actual_damage = self.enemy.take_damage(damage)
                print(f"\n{self.player.name} attacks {self.enemy.name} for {actual_damage} damage!")
                time.sleep(0.5)
                return True

            elif choice == "2":
                damage, message = self.player.special_ability(self.enemy)
                print(f"\n{message}")
                if damage > 0:
                    actual_damage = self.enemy.take_damage(damage)
                    print(f"{self.enemy.name} takes {actual_damage} damage!")
                    time.sleep(0.5)
                    return True
                else:
                    print("Try a different action.")
                    continue

            elif choice == "3":
                if self.use_item():
                    return True
                else:
                    continue

            elif choice == "4":
                if self.attempt_run():
                    return False
                else:
                    print("Failed to escape! Enemy attacks!")
                    time.sleep(0.5)
                    return True
            else:
                print("Invalid choice! Try again.")

    def use_item(self) -> bool:
        """Use an item from inventory. Returns True if turn was used"""
        potions = [item for item in self.player.inventory if item.item_type == "potion"]

        if not potions:
            print("You have no potions to use!")
            return False

        print("\nAvailable potions:")
        for i, potion in enumerate(potions, 1):
            print(f"{i}. {potion.name} - Heals {potion.value} HP")
        print(f"{len(potions) + 1}. Cancel")

        choice = input(f"\nChoose potion (1-{len(potions) + 1}): ").strip()

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(potions):
                potion = potions[choice_num - 1]
                self.player.heal(potion.value)
                self.player.remove_item(potion)
                print(f"\n{self.player.name} uses {potion.name} and recovers {potion.value} HP!")
                print(f"HP: {self.player.hp}/{self.player.max_hp}")
                time.sleep(0.5)
                return True
            elif choice_num == len(potions) + 1:
                return False
        except ValueError:
            pass

        print("Invalid choice!")
        return False

    def attempt_run(self) -> bool:
        """Attempt to run from combat"""
        escape_chance = min(80, 40 + (self.player.agility - self.enemy.agility) * 5)
        if random.randint(1, 100) <= escape_chance:
            print(f"\n{self.player.name} successfully escaped!")
            return True
        return False

    def enemy_turn(self):
        """Handle enemy's turn"""
        print(f"\n{self.enemy.name}'s turn!")
        time.sleep(0.5)

        # Enemy AI: 80% attack, 20% strong attack
        if random.random() < 0.8:
            damage = self.enemy.attack()
            actual_damage = self.player.take_damage(damage)
            print(f"{self.enemy.name} attacks for {actual_damage} damage!")
        else:
            damage = int(self.enemy.attack() * 1.5)
            actual_damage = self.player.take_damage(damage)
            print(f"{self.enemy.name} uses a powerful attack for {actual_damage} damage!")

        time.sleep(0.5)

    def start_combat(self) -> bool:
        """
        Start combat encounter
        Returns True if player won, False if player lost or ran away
        """
        print(f"\n{'#'*60}")
        print(f"COMBAT START: {self.player.name} vs {self.enemy.name} (Level {self.enemy.level})")
        print(f"{'#'*60}")
        time.sleep(0.5)

        while self.player.is_alive() and self.enemy.is_alive():
            self.display_combat_status()

            # Player turn
            continue_combat = self.player_turn()
            if not continue_combat:  # Player ran away
                return False

            if not self.enemy.is_alive():
                break

            # Enemy turn
            self.enemy_turn()

            if not self.player.is_alive():
                break

            self.turn += 1

        # Combat ended
        print(f"\n{'='*60}")
        if self.player.is_alive():
            print(f"VICTORY! {self.enemy.name} has been defeated!")
            gold, exp = self.enemy.get_reward()
            self.player.gold += gold
            old_level = self.player.level
            self.player.add_experience(exp)
            print(f"\nRewards: {gold} gold, {exp} experience")

            if self.player.level > old_level:
                print(f"\n*** LEVEL UP! {self.player.name} is now level {self.player.level}! ***")
                print(f"HP and MP fully restored!")

            # Random item drop
            if random.random() < 0.4:  # 40% chance
                loot = self.generate_loot()
                self.player.add_item(loot)
                print(f"Found item: {loot.name}")

            print(f"{'='*60}")
            time.sleep(1)
            return True
        else:
            print(f"DEFEAT! {self.player.name} has been defeated by {self.enemy.name}!")
            print(f"{'='*60}")
            time.sleep(1)
            return False

    def generate_loot(self) -> Item:
        """Generate random loot"""
        loot_table = [
            Item("Health Potion", "potion", 30, "Restores 30 HP"),
            Item("Greater Health Potion", "potion", 50, "Restores 50 HP"),
            Item("Mana Potion", "potion", 20, "Restores 20 MP"),
        ]
        return random.choice(loot_table)


def create_random_enemy(player_level: int) -> Enemy:
    """Create a random enemy appropriate for player level"""
    enemy_types = [
        ("Goblin", player_level),
        ("Wolf", player_level),
        ("Bandit", player_level),
        ("Skeleton", player_level + 1),
        ("Orc Warrior", player_level + 1),
        ("Dark Mage", player_level + 2),
    ]

    name, level = random.choice(enemy_types)
    return Enemy(name, max(1, level + random.randint(-1, 1)))
