"""
World module for the RPG game
Defines locations, NPCs, and shops
"""

from character import Item, Player
from typing import List, Dict, Optional


class Shop:
    """Merchant shop for buying and selling items"""
    def __init__(self, name: str, items: List[Item]):
        self.name = name
        self.items = items

    def display_shop(self):
        """Display shop inventory"""
        print(f"\n{'='*60}")
        print(f"Welcome to {self.name}!")
        print(f"{'='*60}")
        print("\nAvailable items:")
        for i, item in enumerate(self.items, 1):
            price = self.get_buy_price(item)
            print(f"{i}. {item.name} ({item.item_type}) - {price} gold")
            print(f"   {item.description}")

    def get_buy_price(self, item: Item) -> int:
        """Get buying price for an item"""
        base_prices = {
            "weapon": lambda v: v * 15,
            "armor": lambda v: v * 12,
            "potion": lambda v: v * 2,
        }
        return base_prices.get(item.item_type, lambda v: v * 10)(item.value)

    def get_sell_price(self, item: Item) -> int:
        """Get selling price for an item"""
        return int(self.get_buy_price(item) * 0.5)

    def buy_item(self, player: Player, item_index: int) -> bool:
        """Player buys an item"""
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            price = self.get_buy_price(item)
            if player.gold >= price:
                player.gold -= price
                player.add_item(item)
                print(f"\nPurchased {item.name} for {price} gold!")
                return True
            else:
                print(f"\nNot enough gold! Need {price} gold, have {player.gold} gold.")
                return False
        return False

    def sell_item(self, player: Player, item: Item) -> bool:
        """Player sells an item"""
        price = self.get_sell_price(item)
        player.gold += price
        player.remove_item(item)
        print(f"\nSold {item.name} for {price} gold!")
        return True


class Quest:
    """Represents a quest"""
    def __init__(self, name: str, description: str, objectives: str,
                 reward_gold: int, reward_exp: int, reward_item: Optional[Item] = None):
        self.name = name
        self.description = description
        self.objectives = objectives
        self.reward_gold = reward_gold
        self.reward_exp = reward_exp
        self.reward_item = reward_item
        self.completed = False
        self.active = False

    def display(self):
        """Display quest information"""
        status = "COMPLETED" if self.completed else "ACTIVE" if self.active else "AVAILABLE"
        print(f"\n[{status}] {self.name}")
        print(f"Description: {self.description}")
        print(f"Objectives: {self.objectives}")
        print(f"Rewards: {self.reward_gold} gold, {self.reward_exp} exp", end="")
        if self.reward_item:
            print(f", {self.reward_item.name}")
        else:
            print()


class Location:
    """Represents a location in the game world"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.shop: Optional[Shop] = None
        self.connected_locations: List[str] = []
        self.danger_level = 1  # For enemy encounters

    def set_shop(self, shop: Shop):
        """Set shop for this location"""
        self.shop = shop

    def add_connection(self, location_name: str):
        """Add connected location"""
        if location_name not in self.connected_locations:
            self.connected_locations.append(location_name)

    def display(self):
        """Display location information"""
        print(f"\n{'='*60}")
        print(f"Location: {self.name}")
        print(f"{'='*60}")
        print(f"{self.description}")
        if self.shop:
            print(f"\nA merchant's shop is here: {self.shop.name}")
        if self.connected_locations:
            print(f"\nConnected areas: {', '.join(self.connected_locations)}")
        print(f"{'='*60}")


class GameWorld:
    """Manages the game world"""
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.quests: List[Quest] = []
        self.current_location: Optional[Location] = None
        self.setup_world()

    def setup_world(self):
        """Initialize the game world"""
        # Create locations
        village = Location(
            "Riverside Village",
            "A peaceful village by the river. Wooden houses line cobblestone streets. "
            "The villagers go about their daily business, though worry shows on their faces."
        )

        forest = Location(
            "Dark Forest",
            "Dense trees block most of the sunlight. Strange sounds echo through the woods. "
            "Dangerous creatures are known to lurk here."
        )
        forest.danger_level = 2

        cave = Location(
            "Ancient Cave",
            "A mysterious cave with ancient markings on the walls. "
            "The air is cold and damp. Treasures may lie within, but so do dangers."
        )
        cave.danger_level = 3

        ruins = Location(
            "Abandoned Ruins",
            "Once a great castle, now crumbling ruins. "
            "Undead creatures are said to haunt these halls."
        )
        ruins.danger_level = 4

        mountains = Location(
            "Misty Mountains",
            "Towering peaks shrouded in mist. The path is treacherous. "
            "Only the bravest adventurers dare venture here."
        )
        mountains.danger_level = 5

        # Connect locations
        village.add_connection("Dark Forest")
        village.add_connection("Ancient Cave")
        forest.add_connection("Riverside Village")
        forest.add_connection("Abandoned Ruins")
        cave.add_connection("Riverside Village")
        cave.add_connection("Misty Mountains")
        ruins.add_connection("Dark Forest")
        ruins.add_connection("Misty Mountains")
        mountains.add_connection("Ancient Cave")
        mountains.add_connection("Abandoned Ruins")

        # Create shop in village
        village_shop = Shop(
            "The Rusty Blade",
            [
                Item("Steel Sword", "weapon", 15, "A well-crafted steel blade"),
                Item("Battle Axe", "weapon", 20, "A heavy two-handed axe"),
                Item("Magic Wand", "weapon", 18, "A wand infused with arcane power"),
                Item("Leather Armor", "armor", 10, "Light but sturdy leather armor"),
                Item("Chain Mail", "armor", 15, "Heavy protective chain armor"),
                Item("Health Potion", "potion", 30, "Restores 30 HP"),
                Item("Greater Health Potion", "potion", 50, "Restores 50 HP"),
                Item("Mana Potion", "potion", 20, "Restores 20 MP"),
            ]
        )
        village.set_shop(village_shop)

        # Add locations to world
        self.locations["Riverside Village"] = village
        self.locations["Dark Forest"] = forest
        self.locations["Ancient Cave"] = cave
        self.locations["Abandoned Ruins"] = ruins
        self.locations["Misty Mountains"] = mountains

        # Set starting location
        self.current_location = village

        # Create quests
        self.quests = [
            Quest(
                "The Goblin Menace",
                "Goblins have been raiding the village farms. Defeat 3 enemies to help protect the village.",
                "Defeat 3 enemies",
                100,
                150,
                Item("Ring of Protection", "armor", 5, "A magical ring that increases defense")
            ),
            Quest(
                "Cave Explorer",
                "Explore the Ancient Cave and discover what lies within.",
                "Visit the Ancient Cave",
                50,
                100
            ),
            Quest(
                "Mountain Climber",
                "Reach the peak of the Misty Mountains.",
                "Visit the Misty Mountains",
                150,
                200,
                Item("Amulet of Strength", "weapon", 12, "An amulet that increases attack power")
            ),
        ]

    def travel_to(self, location_name: str) -> bool:
        """Travel to a different location"""
        if location_name in self.current_location.connected_locations:
            if location_name in self.locations:
                self.current_location = self.locations[location_name]
                return True
        return False

    def get_active_quests(self) -> List[Quest]:
        """Get list of active quests"""
        return [q for q in self.quests if q.active and not q.completed]

    def get_available_quests(self) -> List[Quest]:
        """Get list of available quests"""
        return [q for q in self.quests if not q.active and not q.completed]

    def get_completed_quests(self) -> List[Quest]:
        """Get list of completed quests"""
        return [q for q in self.quests if q.completed]
