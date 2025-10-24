#!/usr/bin/env python3
"""
GUI version of the RPG game using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import random
from character import Player, Item
from combat import Combat, create_random_enemy
from world import GameWorld, Shop
from save_system import SaveSystem


class RPGGameGUI:
    """Main GUI class for the RPG game"""

    def __init__(self, root):
        self.root = root
        self.root.title("RPG Adventure")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')

        self.player = None
        self.world = None
        self.save_system = SaveSystem()
        self.enemies_defeated = 0
        self.combat_active = False

        # Configure style
        self.setup_styles()

        # Show main menu
        self.show_main_menu()

    def setup_styles(self):
        """Setup custom styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        button_bg = '#3a3a3a'
        button_active = '#4a4a4a'

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('TButton', background=button_bg, foreground=fg_color,
                       borderwidth=1, font=('Arial', 10))
        style.map('TButton', background=[('active', button_active)])
        style.configure('Action.TButton', font=('Arial', 11, 'bold'), padding=10)

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """Display the main menu"""
        self.clear_window()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both')

        # Title
        title_label = ttk.Label(main_frame, text="RPG ADVENTURE",
                               style='Title.TLabel')
        title_label.pack(pady=50)

        # Subtitle
        subtitle = ttk.Label(main_frame, text="A Classic RPG Experience",
                            font=('Arial', 12, 'italic'))
        subtitle.pack(pady=10)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=50)

        new_game_btn = ttk.Button(button_frame, text="New Game",
                                  command=self.show_character_creation,
                                  style='Action.TButton', width=20)
        new_game_btn.pack(pady=10)

        load_game_btn = ttk.Button(button_frame, text="Load Game",
                                   command=self.show_load_game,
                                   style='Action.TButton', width=20)
        load_game_btn.pack(pady=10)

        exit_btn = ttk.Button(button_frame, text="Exit",
                             command=self.root.quit,
                             style='Action.TButton', width=20)
        exit_btn.pack(pady=10)

    def show_character_creation(self):
        """Display character creation screen"""
        self.clear_window()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title = ttk.Label(main_frame, text="Character Creation",
                         style='Header.TLabel')
        title.pack(pady=20)

        # Name input
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(pady=10)

        ttk.Label(name_frame, text="Character Name:").pack(side='left', padx=5)
        name_entry = ttk.Entry(name_frame, width=30, font=('Arial', 12))
        name_entry.pack(side='left', padx=5)
        name_entry.insert(0, "Hero")

        # Class selection
        class_frame = ttk.Frame(main_frame)
        class_frame.pack(pady=20)

        ttk.Label(class_frame, text="Choose Your Class:",
                 style='Header.TLabel').pack(pady=10)

        class_var = tk.StringVar(value="Warrior")

        # Warrior
        warrior_frame = ttk.Frame(class_frame)
        warrior_frame.pack(pady=5, fill='x')
        ttk.Radiobutton(warrior_frame, text="Warrior", variable=class_var,
                       value="Warrior").pack(side='left')
        ttk.Label(warrior_frame,
                 text="High strength and HP, powerful physical attacks",
                 font=('Arial', 9, 'italic')).pack(side='left', padx=20)

        # Mage
        mage_frame = ttk.Frame(class_frame)
        mage_frame.pack(pady=5, fill='x')
        ttk.Radiobutton(mage_frame, text="Mage", variable=class_var,
                       value="Mage").pack(side='left')
        ttk.Label(mage_frame,
                 text="High intelligence and MP, devastating magic attacks",
                 font=('Arial', 9, 'italic')).pack(side='left', padx=20)

        # Rogue
        rogue_frame = ttk.Frame(class_frame)
        rogue_frame.pack(pady=5, fill='x')
        ttk.Radiobutton(rogue_frame, text="Rogue", variable=class_var,
                       value="Rogue").pack(side='left')
        ttk.Label(rogue_frame,
                 text="High agility, critical hits and evasion",
                 font=('Arial', 9, 'italic')).pack(side='left', padx=20)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)

        def create_character():
            name = name_entry.get().strip() or "Hero"
            char_class = class_var.get()
            self.player = Player(name, char_class)
            self.world = GameWorld()
            self.enemies_defeated = 0
            messagebox.showinfo("Character Created",
                              f"{name} the {char_class} has been created!")
            self.show_game_screen()

        ttk.Button(button_frame, text="Create Character",
                  command=create_character,
                  style='Action.TButton', width=20).pack(side='left', padx=10)

        ttk.Button(button_frame, text="Back",
                  command=self.show_main_menu,
                  style='Action.TButton', width=20).pack(side='left', padx=10)

    def show_load_game(self):
        """Display load game screen"""
        saves = self.save_system.list_saves()

        if not saves:
            messagebox.showinfo("No Saves", "No saved games found!")
            return

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Game")
        dialog.geometry("400x300")
        dialog.configure(bg='#2b2b2b')

        ttk.Label(dialog, text="Select Save File:",
                 style='Header.TLabel').pack(pady=10)

        # Listbox with saves
        listbox = tk.Listbox(dialog, font=('Arial', 11),
                            bg='#3a3a3a', fg='white',
                            selectmode='single', height=10)
        listbox.pack(pady=10, padx=20, fill='both', expand=True)

        for save in saves:
            listbox.insert(tk.END, save)

        def load_selected():
            selection = listbox.curselection()
            if selection:
                save_name = saves[selection[0]]
                game_data = self.save_system.load_game(save_name)
                if game_data:
                    self.player = game_data["player"]
                    self.world = game_data["world"]
                    self.enemies_defeated = game_data.get("enemies_defeated", 0)
                    dialog.destroy()
                    self.show_game_screen()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Load", command=load_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def show_game_screen(self):
        """Display main game screen"""
        self.clear_window()

        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(expand=True, fill='both')

        # Top section - Stats and Info
        top_frame = ttk.Frame(main_container)
        top_frame.pack(side='top', fill='x', padx=10, pady=5)

        # Stats panel
        stats_frame = ttk.LabelFrame(top_frame, text="Character Stats", padding=10)
        stats_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.stats_text = tk.Text(stats_frame, height=8, width=50,
                                 bg='#3a3a3a', fg='white',
                                 font=('Courier', 9), wrap='word')
        self.stats_text.pack(fill='both', expand=True)

        # Location panel
        location_frame = ttk.LabelFrame(top_frame, text="Current Location", padding=10)
        location_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.location_text = tk.Text(location_frame, height=8, width=50,
                                    bg='#3a3a3a', fg='white',
                                    font=('Arial', 9), wrap='word')
        self.location_text.pack(fill='both', expand=True)

        # Middle section - Game log
        log_frame = ttk.LabelFrame(main_container, text="Game Log", padding=10)
        log_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)

        self.game_log = scrolledtext.ScrolledText(log_frame, height=15,
                                                  bg='#3a3a3a', fg='#00ff00',
                                                  font=('Courier', 9), wrap='word')
        self.game_log.pack(fill='both', expand=True)
        self.game_log.config(state='disabled')

        # Bottom section - Actions
        action_frame = ttk.LabelFrame(main_container, text="Actions", padding=10)
        action_frame.pack(side='top', fill='x', padx=10, pady=5)

        # Create action buttons
        btn_frame1 = ttk.Frame(action_frame)
        btn_frame1.pack(pady=2)

        ttk.Button(btn_frame1, text="View Stats", command=self.view_stats,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame1, text="Inventory", command=self.show_inventory,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame1, text="Explore", command=self.explore,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame1, text="Travel", command=self.show_travel,
                  width=15).pack(side='left', padx=3)

        btn_frame2 = ttk.Frame(action_frame)
        btn_frame2.pack(pady=2)

        ttk.Button(btn_frame2, text="Visit Shop", command=self.show_shop,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame2, text="Quests", command=self.show_quests,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame2, text="Rest", command=self.rest,
                  width=15).pack(side='left', padx=3)
        ttk.Button(btn_frame2, text="Save Game", command=self.save_game,
                  width=15).pack(side='left', padx=3)

        btn_frame3 = ttk.Frame(action_frame)
        btn_frame3.pack(pady=2)

        ttk.Button(btn_frame3, text="Main Menu", command=self.return_to_menu,
                  width=15).pack(side='left', padx=3)

        # Update displays
        self.update_displays()
        self.log_message("Welcome to RPG Adventure!")
        self.log_message(f"You are at {self.world.current_location.name}")

    def update_displays(self):
        """Update stats and location displays"""
        if not self.player or not self.world:
            return

        # Update stats
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        stats = f"{self.player.name} - Level {self.player.level} {self.player.char_class}\n"
        stats += f"{'='*40}\n"
        stats += f"HP: {self.player.hp}/{self.player.max_hp}\n"
        stats += f"MP: {self.player.mp}/{self.player.max_mp}\n"
        stats += f"EXP: {self.player.experience}/{self.player.level * 100}\n"
        stats += f"Gold: {self.player.gold}\n"
        stats += f"{'='*40}\n"
        stats += f"STR: {self.player.strength}  INT: {self.player.intelligence}\n"
        stats += f"AGI: {self.player.agility}  DEF: {self.player.defense}\n"
        if self.player.equipped_weapon:
            stats += f"\nWeapon: {self.player.equipped_weapon.name}\n"
        if self.player.equipped_armor:
            stats += f"Armor: {self.player.equipped_armor.name}\n"
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state='disabled')

        # Update location
        self.location_text.config(state='normal')
        self.location_text.delete(1.0, tk.END)
        loc = f"{self.world.current_location.name}\n"
        loc += f"{'='*40}\n"
        loc += f"{self.world.current_location.description}\n"
        if self.world.current_location.shop:
            loc += f"\n[Shop Available: {self.world.current_location.shop.name}]\n"
        if self.world.current_location.connected_locations:
            loc += f"\nConnected Areas:\n"
            for conn in self.world.current_location.connected_locations:
                loc += f"  - {conn}\n"
        self.location_text.insert(1.0, loc)
        self.location_text.config(state='disabled')

    def log_message(self, message):
        """Add message to game log"""
        self.game_log.config(state='normal')
        self.game_log.insert(tk.END, message + "\n")
        self.game_log.see(tk.END)
        self.game_log.config(state='disabled')

    def view_stats(self):
        """Show detailed stats"""
        self.log_message("\n" + "="*50)
        self.log_message(f"{self.player.name} - Level {self.player.level} {self.player.char_class}")
        self.log_message("="*50)
        self.log_message(f"HP: {self.player.hp}/{self.player.max_hp} | MP: {self.player.mp}/{self.player.max_mp}")
        self.log_message(f"Experience: {self.player.experience}/{self.player.level * 100}")
        self.log_message(f"Strength: {self.player.strength} | Intelligence: {self.player.intelligence}")
        self.log_message(f"Agility: {self.player.agility} | Defense: {self.player.defense}")
        self.log_message(f"Gold: {self.player.gold}")
        if self.player.equipped_weapon:
            self.log_message(f"Weapon: {self.player.equipped_weapon.name} (+{self.player.equipped_weapon.value} damage)")
        if self.player.equipped_armor:
            self.log_message(f"Armor: {self.player.equipped_armor.name} (+{self.player.equipped_armor.value} defense)")
        self.log_message("="*50)

    def show_inventory(self):
        """Show inventory dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Inventory")
        dialog.geometry("600x400")
        dialog.configure(bg='#2b2b2b')

        ttk.Label(dialog, text=f"Gold: {self.player.gold}",
                 style='Header.TLabel').pack(pady=10)

        if not self.player.inventory:
            ttk.Label(dialog, text="Your inventory is empty!").pack(pady=20)
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            return

        # Listbox with items
        listbox = tk.Listbox(dialog, font=('Arial', 10),
                            bg='#3a3a3a', fg='white',
                            selectmode='single', height=15)
        listbox.pack(pady=10, padx=20, fill='both', expand=True)

        for item in self.player.inventory:
            listbox.insert(tk.END, f"{item.name} ({item.item_type}) - {item.description}")

        def use_item():
            selection = listbox.curselection()
            if selection:
                item = self.player.inventory[selection[0]]
                if item.item_type == "weapon":
                    self.player.equip_weapon(item)
                    self.log_message(f"Equipped {item.name}!")
                    self.update_displays()
                    dialog.destroy()
                elif item.item_type == "armor":
                    self.player.equip_armor(item)
                    self.log_message(f"Equipped {item.name}!")
                    self.update_displays()
                    dialog.destroy()
                elif item.item_type == "potion":
                    self.player.heal(item.value)
                    self.player.remove_item(item)
                    self.log_message(f"Used {item.name}! Restored {item.value} HP.")
                    self.log_message(f"Current HP: {self.player.hp}/{self.player.max_hp}")
                    self.update_displays()
                    dialog.destroy()
                else:
                    messagebox.showinfo("Cannot Use", "This item cannot be used right now.")

        def drop_item():
            selection = listbox.curselection()
            if selection:
                item = self.player.inventory[selection[0]]
                if messagebox.askyesno("Drop Item", f"Drop {item.name}?"):
                    self.player.remove_item(item)
                    self.log_message(f"Dropped {item.name}")
                    dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Use/Equip", command=use_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Drop", command=drop_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side='left', padx=5)

    def explore(self):
        """Random encounter"""
        self.log_message("\n" + "="*50)
        self.log_message("You explore the area...")

        if random.random() < 0.7:  # 70% encounter chance
            enemy = create_random_enemy(self.player.level)
            enemy.level += self.world.current_location.danger_level - 1
            enemy.adjust_for_level()

            self.log_message(f"A wild {enemy.name} appears!")
            self.start_combat(enemy)
        else:
            self.log_message("Nothing interesting happens...")
            if random.random() < 0.3:
                gold = random.randint(5, 20)
                self.player.gold += gold
                self.log_message(f"You found {gold} gold!")
                self.update_displays()

    def start_combat(self, enemy):
        """Start combat encounter"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Combat!")
        dialog.geometry("700x500")
        dialog.configure(bg='#2b2b2b')
        dialog.grab_set()  # Make modal

        # Combat log
        log_frame = ttk.LabelFrame(dialog, text="Combat Log", padding=10)
        log_frame.pack(pady=10, padx=10, fill='both', expand=True)

        combat_log = scrolledtext.ScrolledText(log_frame, height=15,
                                              bg='#3a3a3a', fg='#ff6666',
                                              font=('Courier', 9), wrap='word')
        combat_log.pack(fill='both', expand=True)
        combat_log.config(state='disabled')

        def log_combat(msg):
            combat_log.config(state='normal')
            combat_log.insert(tk.END, msg + "\n")
            combat_log.see(tk.END)
            combat_log.config(state='disabled')

        # Stats display
        stats_frame = ttk.Frame(dialog)
        stats_frame.pack(pady=5, padx=10, fill='x')

        player_stats = ttk.Label(stats_frame, text="", font=('Arial', 10, 'bold'))
        player_stats.pack(side='left', expand=True)

        enemy_stats = ttk.Label(stats_frame, text="", font=('Arial', 10, 'bold'))
        enemy_stats.pack(side='right', expand=True)

        def update_combat_stats():
            player_stats.config(text=f"{self.player.name}: {self.player.hp}/{self.player.max_hp} HP | {self.player.mp}/{self.player.max_mp} MP")
            enemy_stats.config(text=f"{enemy.name}: {enemy.hp}/{enemy.max_hp} HP")

        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=10)

        attack_btn = ttk.Button(action_frame, text="Attack", width=15)
        attack_btn.pack(side='left', padx=5)

        special_btn = ttk.Button(action_frame, text="Special Ability", width=15)
        special_btn.pack(side='left', padx=5)

        defend_btn = ttk.Button(action_frame, text="Defend", width=15)
        defend_btn.pack(side='left', padx=5)

        run_btn = ttk.Button(action_frame, text="Run", width=15)
        run_btn.pack(side='left', padx=5)

        def player_turn(action):
            """Execute player's turn"""
            # Disable buttons during turn
            attack_btn.config(state='disabled')
            special_btn.config(state='disabled')
            defend_btn.config(state='disabled')
            run_btn.config(state='disabled')

            if action == "attack":
                damage = self.player.attack()
                actual_damage = enemy.take_damage(damage)
                log_combat(f"{self.player.name} attacks for {actual_damage} damage!")

            elif action == "special":
                damage, message = self.player.special_ability(enemy)
                log_combat(message)
                if damage > 0:
                    actual_damage = enemy.take_damage(damage)
                    log_combat(f"{enemy.name} takes {actual_damage} damage!")

            elif action == "defend":
                old_def = self.player.defense
                self.player.defense += 5
                log_combat(f"{self.player.name} takes a defensive stance! (+5 defense)")

                # Enemy turn
                enemy_turn()

                # Restore defense
                self.player.defense = old_def
                update_combat_stats()
                check_combat_end()
                return

            elif action == "run":
                if random.random() < 0.5:
                    log_combat("You successfully escaped!")
                    dialog.after(1000, dialog.destroy)
                    return
                else:
                    log_combat("Failed to escape!")

            update_combat_stats()

            if not enemy.is_alive():
                check_combat_end()
                return

            # Enemy turn
            dialog.after(500, enemy_turn)

        def enemy_turn():
            """Execute enemy's turn"""
            if not enemy.is_alive():
                return

            damage = enemy.attack()
            actual_damage = self.player.take_damage(damage)
            log_combat(f"{enemy.name} attacks for {actual_damage} damage!")

            update_combat_stats()

            dialog.after(500, check_combat_end)

        def check_combat_end():
            """Check if combat has ended"""
            if not enemy.is_alive():
                log_combat(f"\nVictory! {enemy.name} has been defeated!")
                gold, exp = enemy.get_reward()
                self.player.gold += gold
                self.player.add_experience(exp)
                log_combat(f"Gained {gold} gold and {exp} experience!")

                # Level up check
                if self.player.experience >= self.player.level * 100:
                    old_level = self.player.level
                    self.player.level_up()
                    log_combat(f"\n*** LEVEL UP! {self.player.name} is now level {self.player.level}! ***")

                # Random item drop
                if random.random() < 0.3:
                    items = [
                        Item("Health Potion", "potion", 30, "Restores 30 HP"),
                        Item("Mana Potion", "potion", 20, "Restores 20 MP"),
                    ]
                    item = random.choice(items)
                    self.player.add_item(item)
                    log_combat(f"Found {item.name}!")

                self.enemies_defeated += 1
                self.check_quest_progress()
                self.update_displays()
                self.log_message(f"Defeated {enemy.name}!")

                dialog.after(2000, dialog.destroy)

            elif not self.player.is_alive():
                log_combat(f"\nDefeat! {self.player.name} has fallen...")
                self.log_message("You have been defeated!")
                dialog.after(2000, lambda: [dialog.destroy(), self.game_over()])

            else:
                # Re-enable buttons
                attack_btn.config(state='normal')
                special_btn.config(state='normal')
                defend_btn.config(state='normal')
                run_btn.config(state='normal')

        # Bind actions
        attack_btn.config(command=lambda: player_turn("attack"))
        special_btn.config(command=lambda: player_turn("special"))
        defend_btn.config(command=lambda: player_turn("defend"))
        run_btn.config(command=lambda: player_turn("run"))

        # Initialize combat
        log_combat(f"=== COMBAT START ===")
        log_combat(f"{self.player.name} vs {enemy.name} (Level {enemy.level})")
        log_combat("="*40)
        update_combat_stats()

    def show_travel(self):
        """Show travel dialog"""
        if not self.world.current_location.connected_locations:
            messagebox.showinfo("Cannot Travel", "No other locations to travel to from here!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Travel")
        dialog.geometry("400x300")
        dialog.configure(bg='#2b2b2b')

        ttk.Label(dialog, text="Travel to:", style='Header.TLabel').pack(pady=10)

        listbox = tk.Listbox(dialog, font=('Arial', 11),
                            bg='#3a3a3a', fg='white',
                            selectmode='single', height=10)
        listbox.pack(pady=10, padx=20, fill='both', expand=True)

        for loc in self.world.current_location.connected_locations:
            listbox.insert(tk.END, loc)

        def travel():
            selection = listbox.curselection()
            if selection:
                destination = self.world.current_location.connected_locations[selection[0]]
                self.world.travel_to(destination)
                self.log_message(f"\nTraveled to {destination}")
                self.update_displays()
                self.check_quest_progress()
                dialog.destroy()

                # Random encounter
                if random.random() < 0.4:
                    self.log_message("You are ambushed during travel!")
                    enemy = create_random_enemy(self.player.level)
                    self.start_combat(enemy)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Travel", command=travel).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def show_shop(self):
        """Show shop dialog"""
        shop = self.world.current_location.shop
        if not shop:
            messagebox.showinfo("No Shop", "There is no shop at this location!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(shop.name)
        dialog.geometry("700x500")
        dialog.configure(bg='#2b2b2b')

        ttk.Label(dialog, text=shop.name, style='Header.TLabel').pack(pady=10)
        ttk.Label(dialog, text=f"Your Gold: {self.player.gold}").pack(pady=5)

        # Shop items
        items_frame = ttk.LabelFrame(dialog, text="Shop Items", padding=10)
        items_frame.pack(pady=10, padx=10, fill='both', expand=True)

        listbox = tk.Listbox(items_frame, font=('Arial', 10),
                            bg='#3a3a3a', fg='white',
                            selectmode='single', height=15)
        listbox.pack(fill='both', expand=True)

        for item in shop.items:
            price = shop.get_buy_price(item)
            listbox.insert(tk.END, f"{item.name} - {price}g - {item.description}")

        def buy_item():
            selection = listbox.curselection()
            if selection:
                item = shop.items[selection[0]]
                price = shop.get_buy_price(item)
                if self.player.gold >= price:
                    self.player.gold -= price
                    self.player.add_item(item)
                    self.log_message(f"Purchased {item.name} for {price} gold")
                    self.update_displays()
                    messagebox.showinfo("Purchase Complete", f"Purchased {item.name}!")
                else:
                    messagebox.showwarning("Not Enough Gold",
                                         f"Need {price} gold, have {self.player.gold} gold")

        def sell_item():
            if not self.player.inventory:
                messagebox.showinfo("Empty Inventory", "You have nothing to sell!")
                return

            sell_dialog = tk.Toplevel(dialog)
            sell_dialog.title("Sell Items")
            sell_dialog.geometry("500x400")
            sell_dialog.configure(bg='#2b2b2b')

            ttk.Label(sell_dialog, text="Select item to sell:",
                     style='Header.TLabel').pack(pady=10)

            sell_listbox = tk.Listbox(sell_dialog, font=('Arial', 10),
                                     bg='#3a3a3a', fg='white',
                                     selectmode='single', height=15)
            sell_listbox.pack(pady=10, padx=20, fill='both', expand=True)

            for item in self.player.inventory:
                price = shop.get_sell_price(item)
                sell_listbox.insert(tk.END, f"{item.name} - Sell for {price}g")

            def confirm_sell():
                sel = sell_listbox.curselection()
                if sel:
                    item = self.player.inventory[sel[0]]
                    price = shop.get_sell_price(item)
                    self.player.gold += price
                    self.player.remove_item(item)
                    self.log_message(f"Sold {item.name} for {price} gold")
                    self.update_displays()
                    sell_dialog.destroy()

            ttk.Button(sell_dialog, text="Sell", command=confirm_sell).pack(pady=5)
            ttk.Button(sell_dialog, text="Cancel", command=sell_dialog.destroy).pack(pady=5)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Buy", command=buy_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Sell", command=sell_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Leave", command=dialog.destroy).pack(side='left', padx=5)

    def show_quests(self):
        """Show quests dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Quests")
        dialog.geometry("600x500")
        dialog.configure(bg='#2b2b2b')

        ttk.Label(dialog, text="Quests", style='Header.TLabel').pack(pady=10)

        # Quest display
        quest_text = scrolledtext.ScrolledText(dialog, height=20,
                                              bg='#3a3a3a', fg='white',
                                              font=('Arial', 10), wrap='word')
        quest_text.pack(pady=10, padx=10, fill='both', expand=True)

        active = self.world.get_active_quests()
        available = self.world.get_available_quests()
        completed = self.world.get_completed_quests()

        quest_text.insert(tk.END, "=== ACTIVE QUESTS ===\n\n")
        if active:
            for q in active:
                quest_text.insert(tk.END, f"{q.name}\n")
                quest_text.insert(tk.END, f"  {q.description}\n")
                quest_text.insert(tk.END, f"  Objectives: {q.objectives}\n")
                quest_text.insert(tk.END, f"  Rewards: {q.reward_gold}g, {q.reward_exp} XP\n\n")
        else:
            quest_text.insert(tk.END, "No active quests\n\n")

        quest_text.insert(tk.END, "=== AVAILABLE QUESTS ===\n\n")
        if available:
            for i, q in enumerate(available, 1):
                quest_text.insert(tk.END, f"{i}. {q.name}\n")
                quest_text.insert(tk.END, f"  {q.description}\n")
                quest_text.insert(tk.END, f"  Objectives: {q.objectives}\n")
                quest_text.insert(tk.END, f"  Rewards: {q.reward_gold}g, {q.reward_exp} XP\n\n")
        else:
            quest_text.insert(tk.END, "No available quests\n\n")

        quest_text.insert(tk.END, "=== COMPLETED QUESTS ===\n\n")
        if completed:
            for q in completed:
                quest_text.insert(tk.END, f"- {q.name}\n")
        else:
            quest_text.insert(tk.END, "No completed quests\n")

        quest_text.config(state='disabled')

        def accept_quest():
            if not available:
                messagebox.showinfo("No Quests", "No available quests to accept!")
                return

            # Simple dialog to select quest number
            quest_num = tk.simpledialog.askinteger("Accept Quest",
                                                  f"Enter quest number (1-{len(available)}):",
                                                  minvalue=1, maxvalue=len(available))
            if quest_num:
                quest = available[quest_num - 1]
                quest.active = True
                self.log_message(f"Accepted quest: {quest.name}")
                dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        if available:
            ttk.Button(button_frame, text="Accept Quest",
                      command=accept_quest).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side='left', padx=5)

    def check_quest_progress(self):
        """Check quest completion"""
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
                self.log_message("\n" + "="*50)
                self.log_message(f"QUEST COMPLETED: {quest.name}!")
                self.log_message("="*50)
                self.player.gold += quest.reward_gold
                self.player.add_experience(quest.reward_exp)
                self.log_message(f"Rewards: {quest.reward_gold} gold, {quest.reward_exp} exp")
                if quest.reward_item:
                    self.player.add_item(quest.reward_item)
                    self.log_message(f"Received: {quest.reward_item.name}!")
                self.log_message("="*50)
                self.update_displays()
                messagebox.showinfo("Quest Complete!", f"{quest.name} completed!")

    def rest(self):
        """Rest to restore HP/MP"""
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        self.log_message("\nYou rest and recover your strength...")
        self.log_message("HP and MP fully restored!")
        self.update_displays()
        messagebox.showinfo("Rest", "HP and MP fully restored!")

    def save_game(self):
        """Save the game"""
        result = self.save_system.save_game(self.player, self.world, self.enemies_defeated)
        if result:
            self.log_message("Game saved successfully!")
            messagebox.showinfo("Save Game", "Game saved successfully!")

    def game_over(self):
        """Handle game over"""
        msg = f"{self.player.name} has fallen in battle...\n\n"
        msg += f"Level reached: {self.player.level}\n"
        msg += f"Enemies defeated: {self.enemies_defeated}\n"
        msg += f"Gold earned: {self.player.gold}"

        messagebox.showinfo("Game Over", msg)
        self.show_main_menu()

    def return_to_menu(self):
        """Return to main menu"""
        if messagebox.askyesno("Return to Menu", "Return to main menu? (Unsaved progress will be lost)"):
            self.show_main_menu()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = RPGGameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
