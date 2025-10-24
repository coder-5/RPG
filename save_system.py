"""
Save/Load system for the RPG game
Handles saving and loading game state
"""

import json
import os
from typing import Optional, Dict, Any
from character import Player, Item
from world import GameWorld, Quest


class SaveSystem:
    """Handles saving and loading game state"""
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def save_game(self, player: Player, world: GameWorld, enemies_defeated: int) -> bool:
        """Save the current game state"""
        try:
            save_data = {
                "player": self._serialize_player(player),
                "world": self._serialize_world(world),
                "enemies_defeated": enemies_defeated
            }

            save_file = os.path.join(self.save_dir, f"{player.name.lower()}_save.json")
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            print(f"\nGame saved successfully!")
            return True
        except Exception as e:
            print(f"\nError saving game: {e}")
            return False

    def load_game(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Load a saved game"""
        try:
            save_file = os.path.join(self.save_dir, f"{player_name.lower()}_save.json")
            if not os.path.exists(save_file):
                print(f"\nNo save file found for {player_name}")
                return None

            with open(save_file, 'r') as f:
                save_data = json.load(f)

            player = self._deserialize_player(save_data["player"])
            world = self._deserialize_world(save_data["world"])
            enemies_defeated = save_data.get("enemies_defeated", 0)

            print(f"\nGame loaded successfully!")
            return {
                "player": player,
                "world": world,
                "enemies_defeated": enemies_defeated
            }
        except Exception as e:
            print(f"\nError loading game: {e}")
            return None

    def list_saves(self) -> list:
        """List all available save files"""
        saves = []
        if os.path.exists(self.save_dir):
            for file in os.listdir(self.save_dir):
                if file.endswith("_save.json"):
                    player_name = file.replace("_save.json", "").title()
                    saves.append(player_name)
        return saves

    def _serialize_item(self, item: Item) -> Dict:
        """Serialize an item"""
        return {
            "name": item.name,
            "item_type": item.item_type,
            "value": item.value,
            "description": item.description
        }

    def _deserialize_item(self, data: Dict) -> Item:
        """Deserialize an item"""
        return Item(data["name"], data["item_type"], data["value"], data["description"])

    def _serialize_player(self, player: Player) -> Dict:
        """Serialize player data"""
        return {
            "name": player.name,
            "char_class": player.char_class,
            "level": player.level,
            "experience": player.experience,
            "max_hp": player.max_hp,
            "hp": player.hp,
            "max_mp": player.max_mp,
            "mp": player.mp,
            "strength": player.strength,
            "intelligence": player.intelligence,
            "agility": player.agility,
            "defense": player.defense,
            "gold": player.gold,
            "inventory": [self._serialize_item(item) for item in player.inventory],
            "equipped_weapon": self._serialize_item(player.equipped_weapon) if player.equipped_weapon else None,
            "equipped_armor": self._serialize_item(player.equipped_armor) if player.equipped_armor else None
        }

    def _deserialize_player(self, data: Dict) -> Player:
        """Deserialize player data"""
        player = Player(data["name"], data["char_class"])
        player.level = data["level"]
        player.experience = data["experience"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_mp = data["max_mp"]
        player.mp = data["mp"]
        player.strength = data["strength"]
        player.intelligence = data["intelligence"]
        player.agility = data["agility"]
        player.defense = data["defense"]
        player.gold = data["gold"]
        player.inventory = [self._deserialize_item(item) for item in data["inventory"]]
        if data["equipped_weapon"]:
            player.equipped_weapon = self._deserialize_item(data["equipped_weapon"])
        if data["equipped_armor"]:
            player.equipped_armor = self._deserialize_item(data["equipped_armor"])
        return player

    def _serialize_world(self, world: GameWorld) -> Dict:
        """Serialize world data"""
        return {
            "current_location": world.current_location.name if world.current_location else "Riverside Village",
            "quests": [
                {
                    "name": q.name,
                    "completed": q.completed,
                    "active": q.active
                }
                for q in world.quests
            ]
        }

    def _deserialize_world(self, data: Dict) -> GameWorld:
        """Deserialize world data"""
        world = GameWorld()
        if data["current_location"] in world.locations:
            world.current_location = world.locations[data["current_location"]]

        # Restore quest states
        quest_data = {q["name"]: q for q in data["quests"]}
        for quest in world.quests:
            if quest.name in quest_data:
                quest.completed = quest_data[quest.name]["completed"]
                quest.active = quest_data[quest.name]["active"]

        return world
