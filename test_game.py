#!/usr/bin/env python3
"""
Test script to verify RPG game functionality
"""

from character import Player, Enemy, Item
from combat import Combat, create_random_enemy
from world import GameWorld
from save_system import SaveSystem


def test_character_creation():
    """Test character creation"""
    print("Testing character creation...")
    player = Player("TestHero", "Warrior")
    assert player.name == "TestHero"
    assert player.char_class == "Warrior"
    assert player.level == 1
    assert player.is_alive()
    print("✓ Character creation works")


def test_items():
    """Test item system"""
    print("\nTesting item system...")
    sword = Item("Test Sword", "weapon", 10, "A test weapon")
    player = Player("TestHero", "Warrior")

    # Warriors start with equipped weapon, so add item
    player.add_item(sword)
    initial_inv_count = len(player.inventory)

    # Equip the new weapon (old weapon goes to inventory)
    player.equip_weapon(sword)
    assert player.equipped_weapon == sword
    assert player.equipped_weapon.name == "Test Sword"

    print("✓ Item system works")


def test_combat():
    """Test combat system"""
    print("\nTesting combat system...")
    player = Player("TestHero", "Warrior")
    enemy = Enemy("Test Goblin", 1)

    # Test attack
    damage = player.attack()
    assert damage > 0

    # Test taking damage
    enemy.take_damage(damage)
    assert enemy.hp < enemy.max_hp

    # Test special ability
    damage, msg = player.special_ability(enemy)
    assert "Power Strike" in msg or "Not enough MP" in msg

    print("✓ Combat system works")


def test_world():
    """Test world system"""
    print("\nTesting world system...")
    world = GameWorld()
    assert world.current_location is not None
    assert world.current_location.name == "Riverside Village"
    assert len(world.locations) == 5
    assert len(world.quests) == 3

    # Test travel
    success = world.travel_to("Dark Forest")
    assert success
    assert world.current_location.name == "Dark Forest"

    print("✓ World system works")


def test_save_load():
    """Test save/load system"""
    print("\nTesting save/load system...")
    save_sys = SaveSystem("test_saves")
    player = Player("TestHero", "Mage")
    player.level = 5
    player.gold = 500
    world = GameWorld()

    # Test save
    result = save_sys.save_game(player, world, 10)
    assert result

    # Test load
    game_data = save_sys.load_game("TestHero")
    assert game_data is not None
    loaded_player = game_data["player"]
    assert loaded_player.name == "TestHero"
    assert loaded_player.level == 5
    assert loaded_player.gold == 500

    print("✓ Save/load system works")

    # Cleanup
    import os
    import shutil
    if os.path.exists("test_saves"):
        shutil.rmtree("test_saves")


def test_leveling():
    """Test leveling system"""
    print("\nTesting leveling system...")
    player = Player("TestHero", "Rogue")
    initial_level = player.level
    initial_hp = player.max_hp

    player.add_experience(100)
    assert player.level > initial_level
    assert player.max_hp > initial_hp

    print("✓ Leveling system works")


def test_enemy_generation():
    """Test enemy generation"""
    print("\nTesting enemy generation...")
    enemy = create_random_enemy(1)
    assert enemy is not None
    assert enemy.level >= 1
    assert enemy.is_alive()

    gold, exp = enemy.get_reward()
    assert gold > 0
    assert exp > 0

    print("✓ Enemy generation works")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("RPG GAME TEST SUITE")
    print("="*60)

    try:
        test_character_creation()
        test_items()
        test_combat()
        test_world()
        test_save_load()
        test_leveling()
        test_enemy_generation()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
