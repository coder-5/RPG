#!/usr/bin/env python3
"""
Main game file for the RPG
Handles game loop, menus, and player interactions
"""

import sys
import random
from character import Player, Item
from combat import Combat, create_random_enemy
from world import GameWorld, Shop
from save_system import SaveSystem


class RPGGame:
    """Main game class"""
    def __init__(self):
        self.player: Player = None
        self.world: GameWorld = None
        self.save_system = SaveSystem()
        self.game_over = False
        self.enemies_defeated = 0

    def start_game(self):
        """Start the game"""
        self.display_title()
        self.main_menu()

    def display_title(self):
        """Display game title"""
        print("\n" + "="*60)
        print("""
  ____  ____   ____    _    ____  __     _______ _   _ _____ _   _ ____  _____
 |  _ \\|  _ \\ / ___|  / \\  |  _ \\ \\ \\   / / ____| \\ | |_   _| | | |  _ \\| ____|
 | |_) | |_) | |  _  / _ \\ | | | | \\ \\ / /|  _| |  \\| | | | | | | | |_) |  _|
 |  _ <|  __/| |_| |/ ___ \\| |_| |  \\ V / | |___| |\\  | | | | |_| |  _ <| |___
 |_| \\_\\_|    \\____/_/   \\_\\____/    \\_/  |_____|_| \\_| |_|  \\___/|_| \\_\\_____|

        """)
        print("="*60)
        print("Welcome to RPG Adventure!")
        print("="*60 + "\n")

    def main_menu(self):
        """Display main menu"""
        while True:
            print("\n" + "="*60)
            print("MAIN MENU")
            print("="*60)
            print("1. New Game")
            print("2. Load Game")
            print("3. Exit")
            print("="*60)

            choice = input("\nEnter choice (1-3): ").strip()

            if choice == "1":
                self.new_game()
                if self.player:
                    self.game_loop()
            elif choice == "2":
                self.load_game()
                if self.player:
                    self.game_loop()
            elif choice == "3":
                print("\nThanks for playing! Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice! Please try again.")

    def new_game(self):
        """Start a new game"""
        print("\n" + "="*60)
        print("CHARACTER CREATION")
        print("="*60)

        name = input("\nEnter your character's name: ").strip()
        if not name:
            name = "Hero"

        print("\nChoose your class:")
        print("1. Warrior - High strength and HP, powerful physical attacks")
        print("2. Mage - High intelligence and MP, devastating magic attacks")
        print("3. Rogue - High agility, critical hits and evasion")

        while True:
            class_choice = input("\nEnter choice (1-3): ").strip()
            if class_choice == "1":
                char_class = "Warrior"
                break
            elif class_choice == "2":
                char_class = "Mage"
                break
            elif class_choice == "3":
                char_class = "Rogue"
                break
            else:
                print("Invalid choice! Please try again.")

        self.player = Player(name, char_class)
        self.world = GameWorld()
        self.enemies_defeated = 0

        print(f"\n{name} the {char_class} has been created!")
        print(self.player.get_stats())
        input("\nPress Enter to begin your adventure...")

    def load_game(self):
        """Load a saved game"""
        saves = self.save_system.list_saves()

        if not saves:
            print("\nNo saved games found!")
            input("\nPress Enter to continue...")
            return

        print("\n" + "="*60)
        print("LOAD GAME")
        print("="*60)
        print("\nAvailable saves:")
        for i, save_name in enumerate(saves, 1):
            print(f"{i}. {save_name}")
        print(f"{len(saves) + 1}. Cancel")

        choice = input(f"\nEnter choice (1-{len(saves) + 1}): ").strip()

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(saves):
                save_name = saves[choice_num - 1]
                game_data = self.save_system.load_game(save_name)
                if game_data:
                    self.player = game_data["player"]
                    self.world = game_data["world"]
                    self.enemies_defeated = game_data.get("enemies_defeated", 0)
                    print(self.player.get_stats())
                    input("\nPress Enter to continue your adventure...")
        except ValueError:
            print("Invalid choice!")

    def game_loop(self):
        """Main game loop"""
        self.game_over = False

        while not self.game_over:
            self.world.current_location.display()
            self.display_menu()

    def display_menu(self):
        """Display action menu"""
        print("\nWhat would you like to do?")
        print("1. View Stats")
        print("2. Inventory")
        print("3. Explore (Random Encounter)")
        print("4. Travel")
        if self.world.current_location.shop:
            print("5. Visit Shop")
        print("6. Quests")
        print("7. Rest (Restore HP/MP)")
        print("8. Save Game")
        print("9. Main Menu")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            self.view_stats()
        elif choice == "2":
            self.manage_inventory()
        elif choice == "3":
            self.explore()
        elif choice == "4":
            self.travel()
        elif choice == "5" and self.world.current_location.shop:
            self.visit_shop()
        elif choice == "6":
            self.manage_quests()
        elif choice == "7":
            self.rest()
        elif choice == "8":
            self.save_system.save_game(self.player, self.world, self.enemies_defeated)
        elif choice == "9":
            print("\nReturning to main menu...")
            self.game_over = True
        else:
            print("Invalid choice!")

    def view_stats(self):
        """View player stats"""
        print(self.player.get_stats())
        input("\nPress Enter to continue...")

    def manage_inventory(self):
        """Manage inventory"""
        while True:
            print("\n" + "="*60)
            print("INVENTORY")
            print("="*60)
            print(f"Gold: {self.player.gold}")

            if not self.player.inventory:
                print("\nYour inventory is empty!")
                input("\nPress Enter to continue...")
                return

            print("\nItems:")
            for i, item in enumerate(self.player.inventory, 1):
                print(f"{i}. {item}")

            print("\nOptions:")
            print("1. Use/Equip Item")
            print("2. Drop Item")
            print("3. Back")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                self.use_item()
            elif choice == "2":
                self.drop_item()
            elif choice == "3":
                return

    def use_item(self):
        """Use or equip an item"""
        if not self.player.inventory:
            return

        try:
            item_num = int(input(f"\nEnter item number (1-{len(self.player.inventory)}): "))
            if 1 <= item_num <= len(self.player.inventory):
                item = self.player.inventory[item_num - 1]

                if item.item_type == "weapon":
                    self.player.equip_weapon(item)
                    print(f"\nEquipped {item.name}!")
                elif item.item_type == "armor":
                    self.player.equip_armor(item)
                    print(f"\nEquipped {item.name}!")
                elif item.item_type == "potion":
                    self.player.heal(item.value)
                    self.player.remove_item(item)
                    print(f"\nUsed {item.name}! Restored {item.value} HP.")
                    print(f"Current HP: {self.player.hp}/{self.player.max_hp}")
                else:
                    print("\nThis item cannot be used right now.")
                input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid input!")

    def drop_item(self):
        """Drop an item from inventory"""
        if not self.player.inventory:
            return

        try:
            item_num = int(input(f"\nEnter item number to drop (1-{len(self.player.inventory)}): "))
            if 1 <= item_num <= len(self.player.inventory):
                item = self.player.inventory[item_num - 1]
                self.player.remove_item(item)
                print(f"\nDropped {item.name}")
                input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid input!")

    def explore(self):
        """Random encounter"""
        print("\nYou explore the area...")
        input("Press Enter to continue...")

        # Random encounter chance
        if random.random() < 0.7:  # 70% chance
            enemy = create_random_enemy(self.player.level)
            enemy.level += self.world.current_location.danger_level - 1
            enemy.adjust_for_level()

            combat = Combat(self.player, enemy)
            victory = combat.start_combat()

            if victory:
                self.enemies_defeated += 1
                self.check_quest_progress()
            elif not self.player.is_alive():
                self.game_over_screen()
        else:
            print("\nNothing interesting happens...")
            # Random gold find
            if random.random() < 0.3:
                gold = random.randint(5, 20)
                self.player.gold += gold
                print(f"You found {gold} gold!")
            input("\nPress Enter to continue...")

    def travel(self):
        """Travel to another location"""
        if not self.world.current_location.connected_locations:
            print("\nNo other locations to travel to from here!")
            input("\nPress Enter to continue...")
            return

        print("\n" + "="*60)
        print("TRAVEL")
        print("="*60)
        print("\nAvailable destinations:")
        for i, loc in enumerate(self.world.current_location.connected_locations, 1):
            print(f"{i}. {loc}")
        print(f"{len(self.world.current_location.connected_locations) + 1}. Cancel")

        try:
            choice = int(input(f"\nEnter choice (1-{len(self.world.current_location.connected_locations) + 1}): "))
            if 1 <= choice <= len(self.world.current_location.connected_locations):
                destination = self.world.current_location.connected_locations[choice - 1]
                self.world.travel_to(destination)
                print(f"\nTraveling to {destination}...")
                self.check_quest_progress()

                # Random encounter during travel
                if random.random() < 0.4:
                    print("\nYou are ambushed during travel!")
                    enemy = create_random_enemy(self.player.level)
                    combat = Combat(self.player, enemy)
                    victory = combat.start_combat()
                    if victory:
                        self.enemies_defeated += 1
                    elif not self.player.is_alive():
                        self.game_over_screen()

                input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid input!")

    def visit_shop(self):
        """Visit the shop"""
        shop = self.world.current_location.shop
        if not shop:
            return

        while True:
            shop.display_shop()
            print(f"\nYour gold: {self.player.gold}")
            print("\nOptions:")
            print("1. Buy Item")
            print("2. Sell Item")
            print("3. Leave Shop")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                try:
                    item_num = int(input(f"\nEnter item number (1-{len(shop.items)}): "))
                    if 1 <= item_num <= len(shop.items):
                        shop.buy_item(self.player, item_num - 1)
                except ValueError:
                    print("Invalid input!")
            elif choice == "2":
                if not self.player.inventory:
                    print("\nYou have nothing to sell!")
                else:
                    print("\nYour inventory:")
                    for i, item in enumerate(self.player.inventory, 1):
                        price = shop.get_sell_price(item)
                        print(f"{i}. {item.name} - Sell for {price} gold")
                    try:
                        item_num = int(input(f"\nEnter item number (1-{len(self.player.inventory)}): "))
                        if 1 <= item_num <= len(self.player.inventory):
                            item = self.player.inventory[item_num - 1]
                            shop.sell_item(self.player, item)
                    except ValueError:
                        print("Invalid input!")
            elif choice == "3":
                print("\nThank you for your business!")
                return

            input("\nPress Enter to continue...")

    def manage_quests(self):
        """Manage quests"""
        while True:
            print("\n" + "="*60)
            print("QUESTS")
            print("="*60)

            active_quests = self.world.get_active_quests()
            available_quests = self.world.get_available_quests()
            completed_quests = self.world.get_completed_quests()

            if active_quests:
                print("\nActive Quests:")
                for q in active_quests:
                    q.display()

            if available_quests:
                print("\nAvailable Quests:")
                for i, q in enumerate(available_quests, 1):
                    print(f"\n{i}. {q.name}")
                    print(f"   {q.description}")
                    print(f"   Rewards: {q.reward_gold} gold, {q.reward_exp} exp")

            if completed_quests:
                print("\n Completed Quests:")
                for q in completed_quests:
                    print(f"- {q.name}")

            print("\nOptions:")
            if available_quests:
                print("1. Accept Quest")
            print("2. Back")

            choice = input("\nEnter choice: ").strip()

            if choice == "1" and available_quests:
                try:
                    quest_num = int(input(f"\nEnter quest number (1-{len(available_quests)}): "))
                    if 1 <= quest_num <= len(available_quests):
                        quest = available_quests[quest_num - 1]
                        quest.active = True
                        print(f"\nAccepted quest: {quest.name}!")
                        input("\nPress Enter to continue...")
                except ValueError:
                    print("Invalid input!")
            elif choice == "2":
                return

    def check_quest_progress(self):
        """Check if any quest objectives are completed"""
        for quest in self.world.get_active_quests():
            completed = False

            if "Defeat 3 enemies" in quest.objectives and self.enemies_defeated >= 3:
                completed = True
            elif "Visit the Ancient Cave" in quest.objectives and self.world.current_location.name == "Ancient Cave":
                completed = True
            elif "Visit the Misty Mountains" in quest.objectives and self.world.current_location.name == "Misty Mountains":
                completed = True

            if completed:
                quest.completed = True
                quest.active = False
                print(f"\n{'='*60}")
                print(f"QUEST COMPLETED: {quest.name}!")
                print(f"{'='*60}")
                self.player.gold += quest.reward_gold
                self.player.add_experience(quest.reward_exp)
                print(f"Rewards: {quest.reward_gold} gold, {quest.reward_exp} exp")
                if quest.reward_item:
                    self.player.add_item(quest.reward_item)
                    print(f"Received: {quest.reward_item.name}!")
                print(f"{'='*60}")
                input("\nPress Enter to continue...")

    def rest(self):
        """Rest to restore HP and MP"""
        print("\nYou rest and recover your strength...")
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        print(f"HP and MP fully restored!")
        print(f"HP: {self.player.hp}/{self.player.max_hp}")
        print(f"MP: {self.player.mp}/{self.player.max_mp}")
        input("\nPress Enter to continue...")

    def game_over_screen(self):
        """Display game over screen"""
        print("\n" + "="*60)
        print("GAME OVER")
        print("="*60)
        print(f"\n{self.player.name} has fallen in battle...")
        print(f"Level reached: {self.player.level}")
        print(f"Enemies defeated: {self.enemies_defeated}")
        print(f"Gold earned: {self.player.gold}")
        print("\n" + "="*60)
        input("\nPress Enter to return to main menu...")
        self.game_over = True


def main():
    """Main entry point"""
    game = RPGGame()
    game.start_game()


if __name__ == "__main__":
    main()
