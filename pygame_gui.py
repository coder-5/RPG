#!/usr/bin/env python3
"""
Pygame GUI for the RPG game
Features a complete graphical interface with menus, combat, inventory, and more
"""

import pygame
import sys
import random
from character import Player, Item
from combat import create_random_enemy
from world import GameWorld
from save_system import SaveSystem


# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 120, 220)
YELLOW = (240, 220, 50)
DARK_RED = (150, 30, 30)
DARK_GREEN = (30, 150, 30)
DARK_BLUE = (30, 80, 150)
PURPLE = (180, 50, 220)
GOLD = (255, 215, 0)


class Button:
    """A clickable button"""
    def __init__(self, x, y, width, height, text, color=BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class TextBox:
    """A simple text input box"""
    def __init__(self, x, y, width, height, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < 20:
                self.text += event.unicode

    def draw(self, screen, font):
        color = BLUE if self.active else GRAY
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2)

        text_surf = font.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))


class RPGGameGUI:
    """Main game GUI class"""

    # Map constants
    TILE_SIZE = 32
    MAP_WIDTH = 50
    MAP_HEIGHT = 50
    PLAYER_SPEED = 4

    # Map tile types
    TILE_GRASS = 0
    TILE_WATER = 1
    TILE_TREE = 2
    TILE_MOUNTAIN = 3
    TILE_ROAD = 4
    TILE_BUILDING = 5

    # Town layout constants
    TOWN_CENTER_X = 25
    TOWN_CENTER_Y = 25
    TOWN_SIZE = 10

    # Enemy spawn constants
    NUM_ENEMIES = 15

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG Adventure")
        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.header_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.normal_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Game state
        self.state = "main_menu"
        self.player = None
        self.world = None
        self.save_system = SaveSystem()
        self.enemies_defeated = 0

        # Combat state
        self.combat_enemy = None
        self.combat_log = []
        self.combat_turn = "player"

        # UI state
        self.scroll_offset = 0
        self.selected_class = "Warrior"

        # Map state
        self.player_x = 400
        self.player_y = 300
        self.camera_x = 0
        self.camera_y = 0
        self.map_tiles = []
        self.npcs = []
        self.enemies_on_map = []
        self.buildings = []

        self.running = True

    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "main_menu":
                self.handle_main_menu_events(event)
            elif self.state == "character_creation":
                self.handle_character_creation_events(event)
            elif self.state == "map":
                self.handle_map_events(event)
            elif self.state == "game":
                self.handle_game_events(event)
            elif self.state == "combat":
                self.handle_combat_events(event)
            elif self.state == "inventory":
                self.handle_inventory_events(event)
            elif self.state == "shop":
                self.handle_shop_events(event)
            elif self.state == "travel":
                self.handle_travel_events(event)
            elif self.state == "quests":
                self.handle_quests_events(event)

    def update(self):
        """Update game logic"""
        if self.state == "map":
            self.update_map()

    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)

        if self.state == "main_menu":
            self.draw_main_menu()
        elif self.state == "character_creation":
            self.draw_character_creation()
        elif self.state == "map":
            self.draw_map_screen()
        elif self.state == "game":
            self.draw_game_screen()
        elif self.state == "combat":
            self.draw_combat_screen()
        elif self.state == "inventory":
            self.draw_inventory_screen()
        elif self.state == "shop":
            self.draw_shop_screen()
        elif self.state == "travel":
            self.draw_travel_screen()
        elif self.state == "quests":
            self.draw_quests_screen()

        pygame.display.flip()

    # ===== MAIN MENU =====
    def handle_main_menu_events(self, event):
        if not hasattr(self, 'menu_buttons'):
            self.create_main_menu_buttons()

        for i, button in enumerate(self.menu_buttons):
            if button.handle_event(event):
                if i == 0:  # New Game
                    self.state = "character_creation"
                    self.create_character_creation_ui()
                elif i == 1:  # Load Game
                    self.load_game_menu()
                elif i == 2:  # Exit
                    self.running = False

    def create_main_menu_buttons(self):
        button_width = 300
        button_height = 60
        start_y = 300
        spacing = 80

        self.menu_buttons = [
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y,
                   button_width, button_height, "New Game", BLUE),
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing,
                   button_width, button_height, "Load Game", BLUE),
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing * 2,
                   button_width, button_height, "Exit", RED),
        ]

    def draw_main_menu(self):
        # Title
        title = self.title_font.render("RPG ADVENTURE", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.large_font.render("A Classic RPG Experience", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)

        # Buttons
        if not hasattr(self, 'menu_buttons'):
            self.create_main_menu_buttons()
        for button in self.menu_buttons:
            button.draw(self.screen, self.normal_font)

    # ===== CHARACTER CREATION =====
    def create_character_creation_ui(self):
        self.name_textbox = TextBox(SCREEN_WIDTH // 2 - 150, 180, 300, 40, "Hero")
        self.selected_class = "Warrior"

        button_width = 250
        button_height = 50
        start_y = 280
        spacing = 120

        self.class_buttons = [
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y,
                   button_width, button_height, "Warrior", GREEN),
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing,
                   button_width, button_height, "Mage", BLUE),
            Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing * 2,
                   button_width, button_height, "Rogue", PURPLE),
        ]

        self.create_button = Button(SCREEN_WIDTH // 2 - 200, 600,
                                    180, 50, "Create", GREEN)
        self.back_button = Button(SCREEN_WIDTH // 2 + 20, 600,
                                  180, 50, "Back", RED)

    def handle_character_creation_events(self, event):
        self.name_textbox.handle_event(event)

        for i, button in enumerate(self.class_buttons):
            if button.handle_event(event):
                classes = ["Warrior", "Mage", "Rogue"]
                self.selected_class = classes[i]

        if self.create_button.handle_event(event):
            name = self.name_textbox.text or "Hero"
            self.player = Player(name, self.selected_class)
            self.world = GameWorld()
            self.enemies_defeated = 0
            self.init_map()
            self.state = "map"

        if self.back_button.handle_event(event):
            self.state = "main_menu"

    def draw_character_creation(self):
        # Title
        title = self.header_font.render("Character Creation", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Name input
        label = self.large_font.render("Name:", True, WHITE)
        self.screen.blit(label, (SCREEN_WIDTH // 2 - 150, 140))
        self.name_textbox.draw(self.screen, self.normal_font)

        # Class selection
        class_label = self.large_font.render("Choose Your Class:", True, WHITE)
        self.screen.blit(class_label, (SCREEN_WIDTH // 2 - 150, 240))

        # Class descriptions
        descriptions = {
            "Warrior": "High STR & HP, powerful attacks",
            "Mage": "High INT & MP, devastating magic",
            "Rogue": "High AGI, critical hits & evasion"
        }

        for i, (button, (cls, desc)) in enumerate(zip(self.class_buttons, descriptions.items())):
            # Highlight selected class
            if cls == self.selected_class:
                button.color = DARK_GREEN if cls == "Warrior" else (DARK_BLUE if cls == "Mage" else (120, 30, 150))
            else:
                button.color = GREEN if cls == "Warrior" else (BLUE if cls == "Mage" else PURPLE)
            button.draw(self.screen, self.normal_font)

            # Description
            desc_surf = self.small_font.render(desc, True, LIGHT_GRAY)
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH // 2, button.rect.y + 60))
            self.screen.blit(desc_surf, desc_rect)

        # Buttons
        self.create_button.draw(self.screen, self.normal_font)
        self.back_button.draw(self.screen, self.normal_font)

    # ===== MAP SYSTEM =====
    def init_map(self):
        """Initialize the game map"""
        self.generate_terrain()
        self.initialize_player_position()
        self.place_npcs()
        self.spawn_enemies()
        self.initialize_camera()

        if not hasattr(self, 'game_log'):
            self.game_log = []
        self.add_log_message("Welcome to the world! Use WASD or Arrow Keys to move.")
        self.add_log_message("Press I for inventory, M for menu, Q for quests.")

    def generate_terrain(self):
        """Generate the tile-based terrain map"""
        self.map_tiles = []
        town_min = self.TOWN_CENTER_X - self.TOWN_SIZE // 2
        town_max = self.TOWN_CENTER_X + self.TOWN_SIZE // 2

        for y in range(self.MAP_HEIGHT):
            row = []
            for x in range(self.MAP_WIDTH):
                # Create border of trees
                if x < 2 or x > self.MAP_WIDTH - 3 or y < 2 or y > self.MAP_HEIGHT - 3:
                    row.append(self.TILE_TREE)
                # Town area
                elif town_min <= x <= town_max and town_min <= y <= town_max:
                    tile = self._get_town_tile(x, y)
                    row.append(tile)
                # Random water patches
                elif (x + y) % 20 == 0:
                    row.append(self.TILE_WATER)
                # Random trees (10% chance)
                elif random.random() < 0.1:
                    row.append(self.TILE_TREE)
                else:
                    row.append(self.TILE_GRASS)
            self.map_tiles.append(row)

    def _get_town_tile(self, x, y):
        """Get the appropriate tile for a town coordinate"""
        # Roads (cross pattern)
        if (x == self.TOWN_CENTER_X and 22 <= y <= 28) or (22 <= x <= 28 and y == self.TOWN_CENTER_Y):
            return self.TILE_ROAD
        # Shop building
        elif x == 23 and y == 23:
            return self.TILE_BUILDING
        # Inn building
        elif x == 27 and y == 23:
            return self.TILE_BUILDING
        # Guild building
        elif x == self.TOWN_CENTER_X and y == 27:
            return self.TILE_BUILDING
        else:
            return self.TILE_GRASS

    def initialize_player_position(self):
        """Set the player's starting position"""
        self.player_x = self.TOWN_CENTER_X * self.TILE_SIZE
        self.player_y = 15 * self.TILE_SIZE

    def place_npcs(self):
        """Place NPCs on the map"""
        self.npcs = [
            {"x": 23 * self.TILE_SIZE, "y": 22 * self.TILE_SIZE,
             "name": "Shopkeeper", "color": BLUE, "dialog": "Welcome to my shop!"},
            {"x": 27 * self.TILE_SIZE, "y": 22 * self.TILE_SIZE,
             "name": "Innkeeper", "color": PURPLE, "dialog": "Rest here for 10 gold."},
            {"x": self.TOWN_CENTER_X * self.TILE_SIZE, "y": 26 * self.TILE_SIZE,
             "name": "Guild Master", "color": GOLD, "dialog": "I have quests for brave adventurers!"},
            {"x": 20 * self.TILE_SIZE, "y": 15 * self.TILE_SIZE,
             "name": "Village Elder", "color": WHITE, "dialog": "Beware of monsters outside town!"},
        ]

    def spawn_enemies(self):
        """Spawn enemies outside the town area on walkable tiles"""
        self.enemies_on_map = []
        town_min = self.TOWN_CENTER_X - self.TOWN_SIZE // 2
        town_max = self.TOWN_CENTER_X + self.TOWN_SIZE // 2

        # Walkable tiles for enemy spawning
        walkable_tiles = [self.TILE_GRASS, self.TILE_ROAD]

        enemies_spawned = 0
        for i in range(self.NUM_ENEMIES):
            # Prevent infinite loop with attempt counter
            attempts = 0
            max_attempts = 100

            while attempts < max_attempts:
                attempts += 1
                ex_tile = random.randint(5, self.MAP_WIDTH - 6)
                ey_tile = random.randint(5, self.MAP_HEIGHT - 6)

                # Check if outside town area
                if not (town_min <= ex_tile <= town_max and town_min <= ey_tile <= town_max):
                    # Check if tile is walkable
                    if self.map_tiles[ey_tile][ex_tile] in walkable_tiles:
                        self.enemies_on_map.append({
                            "x": ex_tile * self.TILE_SIZE,
                            "y": ey_tile * self.TILE_SIZE,
                            "type": random.choice(["Slime", "Goblin", "Wolf"]),
                            "color": random.choice([RED, DARK_RED, (255, 100, 0)])
                        })
                        enemies_spawned += 1
                        break

            # Warn if couldn't spawn all enemies
            if attempts >= max_attempts:
                print(f"Warning: Could only spawn {enemies_spawned}/{self.NUM_ENEMIES} enemies")
                break

    def initialize_camera(self):
        """Initialize camera to center on player"""
        self.camera_x = self.player_x - SCREEN_WIDTH // 2
        self.camera_y = self.player_y - SCREEN_HEIGHT // 2

    def handle_map_events(self, event):
        """Handle events on the map"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.state = "inventory"
                self.create_inventory_ui()
            elif event.key == pygame.K_m:
                self.state = "game"
                self.create_game_buttons()
            elif event.key == pygame.K_q:
                self.state = "quests"
                self.create_quests_ui()

    def update_map(self):
        """Update map state (player movement, camera)"""
        # Get keys pressed
        keys = pygame.key.get_pressed()

        old_x = self.player_x
        old_y = self.player_y

        # Movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y -= self.PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y += self.PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x -= self.PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x += self.PLAYER_SPEED

        # Only check collisions if player actually moved
        if old_x != self.player_x or old_y != self.player_y:
            # Check collision with tiles
            player_tile_x = int(self.player_x // self.TILE_SIZE)
            player_tile_y = int(self.player_y // self.TILE_SIZE)

            if (0 <= player_tile_y < len(self.map_tiles) and
                0 <= player_tile_x < len(self.map_tiles[0])):
                tile = self.map_tiles[player_tile_y][player_tile_x]
                # Can't walk through water, trees, mountains, buildings
                impassable = [self.TILE_WATER, self.TILE_TREE, self.TILE_MOUNTAIN, self.TILE_BUILDING]
                if tile in impassable:
                    if tile in [self.TILE_WATER, self.TILE_TREE, self.TILE_MOUNTAIN]:
                        self.player_x = old_x
                        self.player_y = old_y
                    elif tile == self.TILE_BUILDING:
                        self.check_building_interaction(player_tile_x, player_tile_y)
                        self.player_x = old_x
                        self.player_y = old_y
            else:
                # Reset position when player moves outside map boundaries
                self.player_x = old_x
                self.player_y = old_y

            # Check collision with NPCs using proper distance calculation
            for npc in self.npcs:
                # Calculate Euclidean distance
                dx = self.player_x - npc["x"]
                dy = self.player_y - npc["y"]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < self.TILE_SIZE:
                    self.add_log_message(f"{npc['name']}: {npc['dialog']}")
                    self.player_x = old_x
                    self.player_y = old_y

            # Check collision with enemies using proper distance calculation
            for enemy in self.enemies_on_map[:]:
                # Calculate Euclidean distance
                dx = self.player_x - enemy["x"]
                dy = self.player_y - enemy["y"]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < self.TILE_SIZE:
                    # Start combat
                    self.add_log_message(f"Encountered a {enemy['type']}!")
                    combat_enemy = create_random_enemy(self.player.level)
                    combat_enemy.name = enemy["type"]
                    self.start_combat(combat_enemy)
                    self.enemies_on_map.remove(enemy)
                    break

            # Update camera to follow player (only when player moves)
            self.camera_x = self.player_x - SCREEN_WIDTH // 2
            self.camera_y = self.player_y - SCREEN_HEIGHT // 2

            # Clamp camera to map bounds
            max_camera_x = len(self.map_tiles[0]) * self.TILE_SIZE - SCREEN_WIDTH
            max_camera_y = len(self.map_tiles) * self.TILE_SIZE - SCREEN_HEIGHT
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def check_building_interaction(self, tile_x, tile_y):
        """Check which building the player is interacting with"""
        if tile_x == 23 and tile_y == 23:
            # Shop
            if self.world.current_location.shop:
                self.state = "shop"
                self.create_shop_ui()
        elif tile_x == 27 and tile_y == 23:
            # Inn
            if self.player.gold >= 10:
                self.player.gold -= 10
                self.player.hp = self.player.max_hp
                self.player.mp = self.player.max_mp
                self.add_log_message("Rested at inn. HP/MP restored! (-10 gold)")
            else:
                self.add_log_message("Need 10 gold to rest at the inn.")
        elif tile_x == 25 and tile_y == 27:
            # Guild
            self.state = "quests"
            self.create_quests_ui()

    def draw_map_screen(self):
        """Draw the map view"""
        # Draw tiles (only visible ones)
        start_col = max(0, int(self.camera_x // self.TILE_SIZE))
        end_col = min(len(self.map_tiles[0]), int((self.camera_x + SCREEN_WIDTH) // self.TILE_SIZE) + 1)
        start_row = max(0, int(self.camera_y // self.TILE_SIZE))
        end_row = min(len(self.map_tiles), int((self.camera_y + SCREEN_HEIGHT) // self.TILE_SIZE) + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = self.map_tiles[row][col]
                x = col * self.TILE_SIZE - self.camera_x
                y = row * self.TILE_SIZE - self.camera_y

                # Draw tile based on type
                if tile == self.TILE_GRASS:
                    pygame.draw.rect(self.screen, (34, 139, 34), (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif tile == self.TILE_WATER:
                    pygame.draw.rect(self.screen, (30, 144, 255), (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif tile == self.TILE_TREE:
                    pygame.draw.rect(self.screen, (0, 100, 0), (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif tile == self.TILE_MOUNTAIN:
                    pygame.draw.rect(self.screen, GRAY, (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif tile == self.TILE_ROAD:
                    pygame.draw.rect(self.screen, (139, 90, 43), (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif tile == self.TILE_BUILDING:
                    pygame.draw.rect(self.screen, (139, 69, 19), (x, y, self.TILE_SIZE, self.TILE_SIZE))

                # Draw grid
                s = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(s, (0, 0, 0, 50), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 1)
                self.screen.blit(s, (x, y))

        # Draw NPCs (only visible ones)
        for npc in self.npcs:
            npc_x = npc["x"] - self.camera_x
            npc_y = npc["y"] - self.camera_y
            # Only draw if on screen
            if -self.TILE_SIZE < npc_x < SCREEN_WIDTH and -self.TILE_SIZE < npc_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, npc["color"],
                                 (int(npc_x + self.TILE_SIZE // 2), int(npc_y + self.TILE_SIZE // 2)),
                                 self.TILE_SIZE // 3)
                # Draw name
                name_surf = self.small_font.render(npc["name"], True, WHITE)
                name_rect = name_surf.get_rect(center=(npc_x + self.TILE_SIZE // 2, npc_y - 10))
                self.screen.blit(name_surf, name_rect)

        # Draw enemies (only visible ones)
        for enemy in self.enemies_on_map:
            enemy_x = enemy["x"] - self.camera_x
            enemy_y = enemy["y"] - self.camera_y
            # Only draw if on screen
            if -self.TILE_SIZE < enemy_x < SCREEN_WIDTH and -self.TILE_SIZE < enemy_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, enemy["color"],
                                 (int(enemy_x + self.TILE_SIZE // 2), int(enemy_y + self.TILE_SIZE // 2)),
                                 self.TILE_SIZE // 3)
                # Draw type
                type_surf = self.small_font.render(enemy["type"][0], True, WHITE)
                type_rect = type_surf.get_rect(center=(enemy_x + self.TILE_SIZE // 2, enemy_y + self.TILE_SIZE // 2))
                self.screen.blit(type_surf, type_rect)

        # Draw player
        player_screen_x = self.player_x - self.camera_x
        player_screen_y = self.player_y - self.camera_y
        pygame.draw.circle(self.screen, YELLOW,
                         (int(player_screen_x + self.TILE_SIZE // 2),
                          int(player_screen_y + self.TILE_SIZE // 2)),
                         self.TILE_SIZE // 2)
        # Draw player indicator
        pygame.draw.circle(self.screen, WHITE,
                         (int(player_screen_x + self.TILE_SIZE // 2),
                          int(player_screen_y + self.TILE_SIZE // 2)),
                         self.TILE_SIZE // 2, 2)

        # Draw HUD
        self.draw_map_hud()

    def draw_map_hud(self):
        """Draw HUD overlay on map"""
        # Top bar with stats
        hud_height = 80
        pygame.draw.rect(self.screen, (0, 0, 0, 200), (0, 0, SCREEN_WIDTH, hud_height))
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, hud_height), 2)

        # Player info
        info_y = 10
        name_text = self.normal_font.render(f"{self.player.name} - Lv{self.player.level} {self.player.char_class}", True, GOLD)
        self.screen.blit(name_text, (10, info_y))

        # HP bar
        hp_x = 10
        hp_y = 45
        hp_width = 200
        hp_height = 20
        hp_percent = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, DARK_RED, (hp_x, hp_y, hp_width, hp_height))
        pygame.draw.rect(self.screen, RED, (hp_x, hp_y, hp_width * hp_percent, hp_height))
        pygame.draw.rect(self.screen, WHITE, (hp_x, hp_y, hp_width, hp_height), 2)
        hp_text = self.small_font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (hp_x + 5, hp_y + 2))

        # MP bar
        mp_x = 220
        mp_y = 45
        mp_width = 200
        mp_height = 20
        mp_percent = self.player.mp / self.player.max_mp
        pygame.draw.rect(self.screen, DARK_BLUE, (mp_x, mp_y, mp_width, mp_height))
        pygame.draw.rect(self.screen, BLUE, (mp_x, mp_y, mp_width * mp_percent, mp_height))
        pygame.draw.rect(self.screen, WHITE, (mp_x, mp_y, mp_width, mp_height), 2)
        mp_text = self.small_font.render(f"MP: {self.player.mp}/{self.player.max_mp}", True, WHITE)
        self.screen.blit(mp_text, (mp_x + 5, mp_y + 2))

        # Gold and EXP
        gold_text = self.normal_font.render(f"Gold: {self.player.gold}", True, GOLD)
        self.screen.blit(gold_text, (450, info_y))

        exp_text = self.small_font.render(f"EXP: {self.player.experience}/{self.player.level * 100}", True, GREEN)
        self.screen.blit(exp_text, (450, hp_y))

        # Controls hint
        controls = self.small_font.render("WASD/Arrows: Move | I: Inventory | Q: Quests | M: Menu", True, LIGHT_GRAY)
        self.screen.blit(controls, (650, info_y + 15))

        # Location
        location_text = self.normal_font.render(f"Location: {self.world.current_location.name}", True, WHITE)
        self.screen.blit(location_text, (SCREEN_WIDTH - 400, info_y))

        # Message log (bottom)
        if hasattr(self, 'game_log') and self.game_log:
            log_bg_height = 100
            pygame.draw.rect(self.screen, (0, 0, 0, 180),
                           (0, SCREEN_HEIGHT - log_bg_height, SCREEN_WIDTH, log_bg_height))
            pygame.draw.rect(self.screen, WHITE,
                           (0, SCREEN_HEIGHT - log_bg_height, SCREEN_WIDTH, log_bg_height), 1)

            y_offset = SCREEN_HEIGHT - log_bg_height + 10
            for msg in self.game_log[-3:]:  # Show last 3 messages
                msg_surf = self.small_font.render(msg, True, GREEN)
                self.screen.blit(msg_surf, (10, y_offset))
                y_offset += 28

    # ===== MAIN GAME SCREEN =====
    def handle_game_events(self, event):
        if not hasattr(self, 'action_buttons'):
            self.create_game_buttons()

        for i, button in enumerate(self.action_buttons):
            if button.handle_event(event):
                if i == 0:  # View Stats
                    self.view_stats()
                elif i == 1:  # Inventory
                    self.state = "inventory"
                    self.create_inventory_ui()
                elif i == 2:  # Explore
                    self.explore()
                elif i == 3:  # Travel
                    self.state = "travel"
                    self.create_travel_ui()
                elif i == 4:  # Shop
                    if self.world.current_location.shop:
                        self.state = "shop"
                        self.create_shop_ui()
                elif i == 5:  # Quests
                    self.state = "quests"
                    self.create_quests_ui()
                elif i == 6:  # Rest
                    self.rest()
                elif i == 7:  # Save
                    self.save_game()
                elif i == 8:  # Menu
                    self.state = "main_menu"

    def create_game_buttons(self):
        button_width = 140
        button_height = 40
        start_x = 20
        start_y = 550
        spacing_x = 150
        spacing_y = 50

        self.action_buttons = [
            Button(start_x, start_y, button_width, button_height, "View Stats", BLUE),
            Button(start_x + spacing_x, start_y, button_width, button_height, "Inventory", BLUE),
            Button(start_x + spacing_x * 2, start_y, button_width, button_height, "Explore", GREEN),
            Button(start_x + spacing_x * 3, start_y, button_width, button_height, "Travel", BLUE),
            Button(start_x, start_y + spacing_y, button_width, button_height, "Shop", PURPLE),
            Button(start_x + spacing_x, start_y + spacing_y, button_width, button_height, "Quests", YELLOW),
            Button(start_x + spacing_x * 2, start_y + spacing_y, button_width, button_height, "Rest", GREEN),
            Button(start_x + spacing_x * 3, start_y + spacing_y, button_width, button_height, "Save", BLUE),
            Button(start_x + spacing_x * 4, start_y + spacing_y, button_width, button_height, "Menu", RED),
        ]

    def draw_game_screen(self):
        if not self.player or not self.world:
            return

        # Title bar
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 60))
        title = self.header_font.render("RPG Adventure", True, GOLD)
        self.screen.blit(title, (20, 10))

        # Stats panel (left side)
        stats_x = 20
        stats_y = 80
        stats_width = 380
        stats_height = 440

        pygame.draw.rect(self.screen, DARK_GRAY, (stats_x, stats_y, stats_width, stats_height))
        pygame.draw.rect(self.screen, WHITE, (stats_x, stats_y, stats_width, stats_height), 2)

        # Stats header
        header = self.large_font.render("Character", True, GOLD)
        self.screen.blit(header, (stats_x + 10, stats_y + 10))

        # Character info
        y_offset = stats_y + 60
        line_height = 30

        stats_text = [
            (f"{self.player.name}", WHITE),
            (f"Level {self.player.level} {self.player.char_class}", YELLOW),
            (f"HP: {self.player.hp}/{self.player.max_hp}", RED),
            (f"MP: {self.player.mp}/{self.player.max_mp}", BLUE),
            (f"EXP: {self.player.experience}/{self.player.level * 100}", GREEN),
            (f"Gold: {self.player.gold}", GOLD),
            ("", WHITE),
            (f"STR: {self.player.strength}  INT: {self.player.intelligence}", WHITE),
            (f"AGI: {self.player.agility}  DEF: {self.player.defense}", WHITE),
        ]

        if self.player.equipped_weapon:
            stats_text.append(("", WHITE))
            stats_text.append((f"Weapon: {self.player.equipped_weapon.name}", LIGHT_GRAY))
        if self.player.equipped_armor:
            stats_text.append((f"Armor: {self.player.equipped_armor.name}", LIGHT_GRAY))

        for text, color in stats_text:
            surf = self.small_font.render(text, True, color)
            self.screen.blit(surf, (stats_x + 20, y_offset))
            y_offset += line_height

        # HP/MP bars
        bar_x = stats_x + 20
        bar_width = stats_width - 40
        bar_height = 20

        # HP bar
        hp_y = stats_y + 110
        hp_percent = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, DARK_RED, (bar_x, hp_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, RED, (bar_x, hp_y, bar_width * hp_percent, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, hp_y, bar_width, bar_height), 1)

        # MP bar
        mp_y = stats_y + 140
        mp_percent = self.player.mp / self.player.max_mp
        pygame.draw.rect(self.screen, DARK_BLUE, (bar_x, mp_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, BLUE, (bar_x, mp_y, bar_width * mp_percent, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, mp_y, bar_width, bar_height), 1)

        # Location panel (right side)
        loc_x = 420
        loc_y = 80
        loc_width = 840
        loc_height = 200

        pygame.draw.rect(self.screen, DARK_GRAY, (loc_x, loc_y, loc_width, loc_height))
        pygame.draw.rect(self.screen, WHITE, (loc_x, loc_y, loc_width, loc_height), 2)

        # Location header
        loc_header = self.large_font.render(self.world.current_location.name, True, GOLD)
        self.screen.blit(loc_header, (loc_x + 10, loc_y + 10))

        # Location description
        desc = self.world.current_location.description
        self.draw_wrapped_text(desc, loc_x + 10, loc_y + 60, loc_width - 20, self.small_font, WHITE)

        # Shop indicator
        if self.world.current_location.shop:
            shop_text = self.small_font.render(f"[Shop: {self.world.current_location.shop.name}]", True, PURPLE)
            self.screen.blit(shop_text, (loc_x + 10, loc_y + loc_height - 30))

        # Game log panel
        log_x = 420
        log_y = 300
        log_width = 840
        log_height = 220

        pygame.draw.rect(self.screen, DARK_GRAY, (log_x, log_y, log_width, log_height))
        pygame.draw.rect(self.screen, WHITE, (log_x, log_y, log_width, log_height), 2)

        log_header = self.large_font.render("Game Log", True, GOLD)
        self.screen.blit(log_header, (log_x + 10, log_y + 10))

        # Draw log messages
        if hasattr(self, 'game_log'):
            y_offset = log_y + 50
            for msg in self.game_log[-8:]:  # Show last 8 messages
                surf = self.small_font.render(msg, True, GREEN)
                self.screen.blit(surf, (log_x + 10, y_offset))
                y_offset += 25

        # Action buttons
        if not hasattr(self, 'action_buttons'):
            self.create_game_buttons()
        for button in self.action_buttons:
            button.draw(self.screen, self.small_font)

    def draw_wrapped_text(self, text, x, y, max_width, font, color):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:3]):  # Max 3 lines
            surf = font.render(line, True, color)
            self.screen.blit(surf, (x, y + i * 25))

    def add_log_message(self, message):
        """Add a message to the game log"""
        if not hasattr(self, 'game_log'):
            self.game_log = []
        self.game_log.append(message)

    def view_stats(self):
        """View detailed stats"""
        self.add_log_message(f"=== {self.player.name} Stats ===")
        self.add_log_message(f"Level {self.player.level} {self.player.char_class}")
        self.add_log_message(f"HP: {self.player.hp}/{self.player.max_hp} | MP: {self.player.mp}/{self.player.max_mp}")

    def explore(self):
        """Explore for random encounters"""
        self.add_log_message("You explore the area...")

        if random.random() < 0.7:  # 70% encounter rate
            enemy = create_random_enemy(self.player.level)
            enemy.level += self.world.current_location.danger_level - 1
            enemy.adjust_for_level()

            self.add_log_message(f"A wild {enemy.name} appears!")
            self.start_combat(enemy)
        else:
            self.add_log_message("Nothing interesting happens...")
            if random.random() < 0.3:
                gold = random.randint(5, 20)
                self.player.gold += gold
                self.add_log_message(f"You found {gold} gold!")

    def rest(self):
        """Rest to restore HP/MP"""
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        self.add_log_message("You rest and recover your strength...")
        self.add_log_message("HP and MP fully restored!")

    def save_game(self):
        """Save the game"""
        self.save_system.save_game(self.player, self.world, self.enemies_defeated)
        self.add_log_message("Game saved!")

    def load_game_menu(self):
        """Show load game menu (simplified)"""
        saves = self.save_system.list_saves()
        if saves and len(saves) > 0:
            # Load first save for simplicity
            game_data = self.save_system.load_game(saves[0])
            if game_data:
                self.player = game_data["player"]
                self.world = game_data["world"]
                self.enemies_defeated = game_data.get("enemies_defeated", 0)
                self.init_map()
                self.state = "map"
                if not hasattr(self, 'game_log'):
                    self.game_log = []
                self.add_log_message("Game loaded!")

    # ===== COMBAT =====
    def start_combat(self, enemy):
        """Start combat with an enemy"""
        self.combat_enemy = enemy
        self.combat_log = []
        self.combat_turn = "player"
        self.state = "combat"
        self.create_combat_buttons()
        self.combat_log.append(f"=== COMBAT START ===")
        self.combat_log.append(f"{self.player.name} vs {enemy.name} (Lv {enemy.level})")

    def create_combat_buttons(self):
        button_width = 200
        button_height = 50
        start_x = 340
        start_y = 550
        spacing = 220

        self.combat_buttons = [
            Button(start_x, start_y, button_width, button_height, "Attack", RED),
            Button(start_x + spacing, start_y, button_width, button_height, "Special Ability", PURPLE),
            Button(start_x, start_y + 70, button_width, button_height, "Defend", BLUE),
            Button(start_x + spacing, start_y + 70, button_width, button_height, "Run", GRAY),
        ]

    def handle_combat_events(self, event):
        if self.combat_turn != "player":
            return

        for i, button in enumerate(self.combat_buttons):
            if button.handle_event(event):
                if i == 0:  # Attack
                    self.combat_attack()
                elif i == 1:  # Special
                    self.combat_special()
                elif i == 2:  # Defend
                    self.combat_defend()
                elif i == 3:  # Run
                    self.combat_run()

    def combat_attack(self):
        """Player attacks"""
        damage = self.player.attack()
        actual_damage = self.combat_enemy.take_damage(damage)
        self.combat_log.append(f"{self.player.name} attacks for {actual_damage} damage!")

        if not self.combat_enemy.is_alive():
            self.combat_victory()
        else:
            self.combat_turn = "enemy"
            pygame.time.set_timer(pygame.USEREVENT, 1000)  # Enemy turn after 1 second

    def combat_special(self):
        """Player uses special ability"""
        damage, message = self.player.special_ability(self.combat_enemy)
        self.combat_log.append(message)

        if damage > 0:
            actual_damage = self.combat_enemy.take_damage(damage)
            self.combat_log.append(f"{self.combat_enemy.name} takes {actual_damage} damage!")

            if not self.combat_enemy.is_alive():
                self.combat_victory()
            else:
                self.combat_turn = "enemy"
                pygame.time.set_timer(pygame.USEREVENT, 1000)
        else:
            self.combat_log.append("Not enough MP!")

    def combat_defend(self):
        """Player defends"""
        self.combat_log.append(f"{self.player.name} takes a defensive stance!")
        old_def = self.player.defense
        self.player.defense += 5

        self.combat_turn = "enemy"
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Special timer for defend

    def combat_run(self):
        """Try to run from combat"""
        if random.random() < 0.5:
            self.combat_log.append("Successfully escaped!")
            pygame.time.set_timer(pygame.USEREVENT + 2, 1500)  # Return to game after delay
        else:
            self.combat_log.append("Failed to escape!")
            self.combat_turn = "enemy"
            pygame.time.set_timer(pygame.USEREVENT, 1000)

    def combat_enemy_turn(self):
        """Enemy's turn"""
        if not self.combat_enemy.is_alive():
            return

        damage = self.combat_enemy.attack()
        actual_damage = self.player.take_damage(damage)
        self.combat_log.append(f"{self.combat_enemy.name} attacks for {actual_damage} damage!")

        if not self.player.is_alive():
            self.combat_defeat()
        else:
            self.combat_turn = "player"

    def combat_victory(self):
        """Player wins combat"""
        self.combat_log.append(f"VICTORY! {self.combat_enemy.name} defeated!")
        gold, exp = self.combat_enemy.get_reward()
        self.player.gold += gold
        old_level = self.player.level
        self.player.add_experience(exp)

        self.combat_log.append(f"Gained {gold} gold and {exp} XP!")

        if self.player.level > old_level:
            self.combat_log.append(f"*** LEVEL UP! Now level {self.player.level}! ***")

        # Random item drop
        if random.random() < 0.3:
            item = Item("Health Potion", "potion", 30, "Restores 30 HP")
            self.player.add_item(item)
            self.combat_log.append(f"Found {item.name}!")

        self.enemies_defeated += 1
        self.check_quest_progress()

        pygame.time.set_timer(pygame.USEREVENT + 2, 3000)  # Return to game after 3 seconds

    def combat_defeat(self):
        """Player loses combat"""
        self.combat_log.append(f"DEFEAT! {self.player.name} has fallen...")
        pygame.time.set_timer(pygame.USEREVENT + 3, 3000)  # Game over after 3 seconds

    def draw_combat_screen(self):
        # Title
        title = self.header_font.render("COMBAT", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)

        # Player stats (left)
        player_x = 100
        player_y = 150

        self.draw_character_combat_card(self.player, player_x, player_y, GREEN)

        # Enemy stats (right)
        enemy_x = SCREEN_WIDTH - 400
        enemy_y = 150

        self.draw_enemy_combat_card(self.combat_enemy, enemy_x, enemy_y, RED)

        # VS text
        vs_text = self.header_font.render("VS", True, YELLOW)
        vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(vs_text, vs_rect)

        # Combat log
        log_x = 200
        log_y = 350
        log_width = 880
        log_height = 180

        pygame.draw.rect(self.screen, DARK_GRAY, (log_x, log_y, log_width, log_height))
        pygame.draw.rect(self.screen, WHITE, (log_x, log_y, log_width, log_height), 2)

        log_title = self.normal_font.render("Combat Log", True, GOLD)
        self.screen.blit(log_title, (log_x + 10, log_y + 10))

        # Draw last combat messages
        y_offset = log_y + 50
        for msg in self.combat_log[-5:]:
            surf = self.small_font.render(msg, True, WHITE)
            self.screen.blit(surf, (log_x + 10, y_offset))
            y_offset += 28

        # Combat buttons
        if self.combat_turn == "player":
            for button in self.combat_buttons:
                button.draw(self.screen, self.normal_font)
        else:
            # Show "Enemy Turn" message
            turn_text = self.large_font.render("Enemy Turn...", True, RED)
            turn_rect = turn_text.get_rect(center=(SCREEN_WIDTH // 2, 590))
            self.screen.blit(turn_text, turn_rect)

    def draw_character_combat_card(self, character, x, y, color):
        """Draw a character card in combat"""
        card_width = 300
        card_height = 180

        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, card_width, card_height))
        pygame.draw.rect(self.screen, color, (x, y, card_width, card_height), 3)

        # Name
        name = self.normal_font.render(character.name, True, WHITE)
        self.screen.blit(name, (x + 10, y + 10))

        # Level
        level = self.small_font.render(f"Level {character.level}", True, YELLOW)
        self.screen.blit(level, (x + 10, y + 40))

        # HP bar
        hp_y = y + 75
        hp_width = card_width - 20
        hp_height = 20
        hp_percent = character.hp / character.max_hp

        pygame.draw.rect(self.screen, DARK_RED, (x + 10, hp_y, hp_width, hp_height))
        pygame.draw.rect(self.screen, RED, (x + 10, hp_y, hp_width * hp_percent, hp_height))
        pygame.draw.rect(self.screen, WHITE, (x + 10, hp_y, hp_width, hp_height), 1)

        hp_text = self.small_font.render(f"HP: {character.hp}/{character.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (x + 10, hp_y + 25))

        # MP bar (if player)
        if isinstance(character, Player):
            mp_y = y + 120
            mp_percent = character.mp / character.max_mp

            pygame.draw.rect(self.screen, DARK_BLUE, (x + 10, mp_y, hp_width, hp_height))
            pygame.draw.rect(self.screen, BLUE, (x + 10, mp_y, hp_width * mp_percent, hp_height))
            pygame.draw.rect(self.screen, WHITE, (x + 10, mp_y, hp_width, hp_height), 1)

            mp_text = self.small_font.render(f"MP: {character.mp}/{character.max_mp}", True, WHITE)
            self.screen.blit(mp_text, (x + 10, mp_y + 25))

    def draw_enemy_combat_card(self, enemy, x, y, color):
        """Draw enemy card in combat"""
        self.draw_character_combat_card(enemy, x, y, color)

    # ===== INVENTORY =====
    def create_inventory_ui(self):
        self.inventory_scroll = 0
        self.close_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80, 200, 50, "Close", RED)

    def handle_inventory_events(self, event):
        if self.close_button.handle_event(event):
            self.state = "map"
            return

        # Handle item clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            item_y = 150
            item_height = 50

            for i, item in enumerate(self.player.inventory):
                item_rect = pygame.Rect(100, item_y + i * (item_height + 10), 1080, item_height)
                if item_rect.collidepoint(x, y):
                    self.use_inventory_item(item)

    def use_inventory_item(self, item):
        """Use an item from inventory"""
        if item.item_type == "weapon":
            self.player.equip_weapon(item)
            self.add_log_message(f"Equipped {item.name}!")
        elif item.item_type == "armor":
            self.player.equip_armor(item)
            self.add_log_message(f"Equipped {item.name}!")
        elif item.item_type == "potion":
            self.player.heal(item.value)
            self.player.remove_item(item)
            self.add_log_message(f"Used {item.name}! Restored {item.value} HP")

        self.state = "map"

    def draw_inventory_screen(self):
        # Title
        title = self.header_font.render("Inventory", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Gold
        gold_text = self.large_font.render(f"Gold: {self.player.gold}", True, GOLD)
        self.screen.blit(gold_text, (100, 100))

        # Items
        if not self.player.inventory:
            empty = self.normal_font.render("Your inventory is empty!", True, WHITE)
            self.screen.blit(empty, (100, 200))
        else:
            item_y = 150
            for item in self.player.inventory:
                # Item box
                item_rect = pygame.Rect(100, item_y, 1080, 50)
                pygame.draw.rect(self.screen, DARK_GRAY, item_rect)
                pygame.draw.rect(self.screen, WHITE, item_rect, 2)

                # Item info
                item_text = self.normal_font.render(f"{item.name} ({item.item_type})", True, WHITE)
                self.screen.blit(item_text, (110, item_y + 5))

                desc_text = self.small_font.render(item.description, True, LIGHT_GRAY)
                self.screen.blit(desc_text, (110, item_y + 28))

                item_y += 60

        # Close button
        self.close_button.draw(self.screen, self.normal_font)

    # ===== TRAVEL =====
    def create_travel_ui(self):
        self.travel_buttons = []
        if self.world.current_location.connected_locations:
            button_width = 400
            button_height = 50
            start_y = 200

            for i, loc in enumerate(self.world.current_location.connected_locations):
                btn = Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + i * 70,
                           button_width, button_height, loc, BLUE)
                self.travel_buttons.append(btn)

        self.cancel_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100,
                                    200, 50, "Cancel", RED)

    def handle_travel_events(self, event):
        if self.cancel_button.handle_event(event):
            self.state = "map"
            return

        for i, button in enumerate(self.travel_buttons):
            if button.handle_event(event):
                destination = self.world.current_location.connected_locations[i]
                self.world.travel_to(destination)
                self.add_log_message(f"Traveled to {destination}")
                self.check_quest_progress()

                # Random encounter
                if random.random() < 0.4:
                    enemy = create_random_enemy(self.player.level)
                    self.add_log_message("Ambushed during travel!")
                    self.start_combat(enemy)
                else:
                    self.state = "map"

    def draw_travel_screen(self):
        # Title
        title = self.header_font.render("Travel", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self.normal_font.render("Choose destination:", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)

        # Travel buttons
        for button in self.travel_buttons:
            button.draw(self.screen, self.normal_font)

        # Cancel button
        self.cancel_button.draw(self.screen, self.normal_font)

    # ===== SHOP =====
    def create_shop_ui(self):
        self.shop_scroll = 0
        self.shop_close_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80,
                                        200, 50, "Leave Shop", RED)

    def handle_shop_events(self, event):
        if self.shop_close_button.handle_event(event):
            self.state = "map"
            return

        # Handle item clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            shop = self.world.current_location.shop
            x, y = event.pos
            item_y = 180
            item_height = 60

            for i, item in enumerate(shop.items):
                item_rect = pygame.Rect(100, item_y + i * (item_height + 10), 1080, item_height)
                if item_rect.collidepoint(x, y):
                    price = shop.get_buy_price(item)
                    if self.player.gold >= price:
                        self.player.gold -= price
                        self.player.add_item(item)
                        self.add_log_message(f"Purchased {item.name} for {price} gold")
                    else:
                        self.add_log_message(f"Not enough gold! Need {price}g")

    def draw_shop_screen(self):
        shop = self.world.current_location.shop

        # Title
        title = self.header_font.render(shop.name, True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Gold
        gold_text = self.large_font.render(f"Your Gold: {self.player.gold}", True, GOLD)
        self.screen.blit(gold_text, (100, 110))

        # Items
        item_y = 180
        for item in shop.items:
            price = shop.get_buy_price(item)

            # Item box
            item_rect = pygame.Rect(100, item_y, 1080, 60)
            pygame.draw.rect(self.screen, DARK_GRAY, item_rect)
            pygame.draw.rect(self.screen, GOLD if self.player.gold >= price else RED,
                           item_rect, 2)

            # Item info
            item_text = self.normal_font.render(f"{item.name} - {price}g", True, WHITE)
            self.screen.blit(item_text, (110, item_y + 5))

            desc_text = self.small_font.render(f"{item.description} ({item.item_type})",
                                              True, LIGHT_GRAY)
            self.screen.blit(desc_text, (110, item_y + 33))

            item_y += 70

        # Close button
        self.shop_close_button.draw(self.screen, self.normal_font)

    # ===== QUESTS =====
    def create_quests_ui(self):
        self.quests_close_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80,
                                          200, 50, "Close", RED)

    def handle_quests_events(self, event):
        if self.quests_close_button.handle_event(event):
            self.state = "map"

    def draw_quests_screen(self):
        # Title
        title = self.header_font.render("Quests", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        y_offset = 120

        # Active quests
        active = self.world.get_active_quests()
        if active:
            header = self.large_font.render("Active Quests", True, GREEN)
            self.screen.blit(header, (100, y_offset))
            y_offset += 40

            for quest in active:
                quest_text = self.normal_font.render(f"- {quest.name}", True, WHITE)
                self.screen.blit(quest_text, (120, y_offset))
                y_offset += 30

                obj_text = self.small_font.render(f"  {quest.objectives}", True, LIGHT_GRAY)
                self.screen.blit(obj_text, (140, y_offset))
                y_offset += 35

        # Available quests
        available = self.world.get_available_quests()
        if available:
            header = self.large_font.render("Available Quests", True, YELLOW)
            self.screen.blit(header, (100, y_offset))
            y_offset += 40

            for quest in available:
                quest_text = self.normal_font.render(f"- {quest.name}", True, WHITE)
                self.screen.blit(quest_text, (120, y_offset))
                y_offset += 30

                desc_text = self.small_font.render(f"  {quest.description}", True, LIGHT_GRAY)
                self.screen.blit(desc_text, (140, y_offset))
                y_offset += 30

                reward_text = self.small_font.render(
                    f"  Rewards: {quest.reward_gold}g, {quest.reward_exp} XP", True, GOLD)
                self.screen.blit(reward_text, (140, y_offset))
                y_offset += 40

        # Completed quests
        completed = self.world.get_completed_quests()
        if completed:
            header = self.large_font.render("Completed Quests", True, BLUE)
            self.screen.blit(header, (100, y_offset))
            y_offset += 40

            for quest in completed:
                quest_text = self.small_font.render(f"- {quest.name}", True, LIGHT_GRAY)
                self.screen.blit(quest_text, (120, y_offset))
                y_offset += 28

        # Close button
        self.quests_close_button.draw(self.screen, self.normal_font)

    def check_quest_progress(self):
        """Check if any quests are completed"""
        for quest in self.world.get_active_quests():
            completed = False

            if "Defeat 3 enemies" in quest.objectives and self.enemies_defeated >= 3:
                completed = True
            elif "Visit the Ancient Cave" in quest.objectives and \
                 self.world.current_location.name == "Ancient Cave":
                completed = True
            elif "Visit the Misty Mountains" in quest.objectives and \
                 self.world.current_location.name == "Misty Mountains":
                completed = True

            if completed:
                quest.completed = True
                quest.active = False
                self.add_log_message(f"QUEST COMPLETE: {quest.name}!")
                self.player.gold += quest.reward_gold
                self.player.add_experience(quest.reward_exp)
                self.add_log_message(f"Rewards: {quest.reward_gold}g, {quest.reward_exp} XP")

                if quest.reward_item:
                    self.player.add_item(quest.reward_item)
                    self.add_log_message(f"Received {quest.reward_item.name}!")

    def update(self):
        """Handle timed events"""
        for event in pygame.event.get([pygame.USEREVENT, pygame.USEREVENT + 1,
                                      pygame.USEREVENT + 2, pygame.USEREVENT + 3]):
            if event.type == pygame.USEREVENT:
                # Enemy turn
                self.combat_enemy_turn()
                pygame.time.set_timer(pygame.USEREVENT, 0)
            elif event.type == pygame.USEREVENT + 1:
                # Defend restore
                self.player.defense -= 5
                self.combat_enemy_turn()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            elif event.type == pygame.USEREVENT + 2:
                # Return to map
                self.state = "map"
                if not hasattr(self, 'game_log'):
                    self.game_log = []
                self.add_log_message(f"Defeated {self.combat_enemy.name}!")
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            elif event.type == pygame.USEREVENT + 3:
                # Game over
                self.state = "main_menu"
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)


def main():
    """Main entry point"""
    game = RPGGameGUI()
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
