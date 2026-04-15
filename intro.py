import pygame
from classes import playerdata


class Introduction:
    def __init__(self, scene):
        self.scene = scene
        self.cursor_pos = [0, 0]

        self.player_sprite = ""
        self.player_name = ""
        self.player_starter = ""
        self.player = playerdata.Player("", "", [], {})

        self.skin_options = ["player", "oldman"]
        self.starter_options = ["peblet", "guardil", "flicklit"]

        self.dialogue_number = 0

        self.intro_dialogue = [
            "Welcome to the world of Pokemon",
            "Tell me a little about yourself",
        ]
        self.starters_dialogue = [
            "Pleased to meet you",
            "I introduce to you the starters of this wonderful land",
        ]
        self.conclusion_dialogue = [
            "Now then, go on and face the world"
        ]

        # confirmation helpers
        self.awaiting_confirmation = False
        self.confirm_cursor = 0          # 0 = Yes, 1 = No
        self.pending_choice = None       # ("skin", "player"), ("name", "Alex"), ("starter", "peblet")

        # name entry helpers
        self.name_buffer = ""

    def begin_confirmation(self, choice_type, value):
        self.awaiting_confirmation = True
        self.confirm_cursor = 0
        self.pending_choice = (choice_type, value)

    def confirm_choice(self):
        if not self.pending_choice:
            return

        choice_type, value = self.pending_choice

        if choice_type == "skin":
            self.player_sprite = value
            playerdata.set_skin(self.player, value)
            self.scene = 3   # move to name scene

        elif choice_type == "name":
            self.player_name = value
            playerdata.choose_name(self.player, value)
            self.scene = 4   # starter intro dialogue
            self.dialogue_number = 0

        elif choice_type == "starter":
            self.player_starter = value
            playerdata.choose_starter(self.player, value)
            self.scene = 6   # conclusion
            self.dialogue_number = 0

        self.awaiting_confirmation = False
        self.pending_choice = None

    def cancel_confirmation(self):
        self.awaiting_confirmation = False
        self.pending_choice = None
        self.confirm_cursor = 0


def check_action(pressed_key, intro):
    # Handle confirmation box first
    if intro.awaiting_confirmation:
        if pressed_key in (pygame.K_LEFT, pygame.K_UP):
            intro.confirm_cursor = (intro.confirm_cursor - 1) % 2
        elif pressed_key in (pygame.K_RIGHT, pygame.K_DOWN):
            intro.confirm_cursor = (intro.confirm_cursor + 1) % 2
        elif pressed_key == pygame.K_z or pressed_key == pygame.K_RETURN:
            if intro.confirm_cursor == 0:
                intro.confirm_choice()
            else:
                intro.cancel_confirmation()
        elif pressed_key == pygame.K_x:
            intro.cancel_confirmation()
        return None, intro.player

    # Main menu
    if intro.scene == 0:
        if pressed_key == pygame.K_DOWN:
            intro.cursor_pos[1] = (intro.cursor_pos[1] + 1) % 2
        elif pressed_key == pygame.K_UP:
            intro.cursor_pos[1] = (intro.cursor_pos[1] - 1) % 2
        elif pressed_key == pygame.K_z or pressed_key == pygame.K_RETURN:
            if intro.cursor_pos[1] == 0:
                pass  # continue
            elif intro.cursor_pos[1] == 1:
                intro.scene = 1
                intro.dialogue_number = 0

    # Dialogue scenes
    elif intro.scene in (1, 4, 6):
        if pressed_key == pygame.K_z or pressed_key == pygame.K_RETURN:
            return advance_dialogue(intro), intro.player

    # Skin select
    elif intro.scene == 2:
        if pressed_key == pygame.K_DOWN:
            intro.cursor_pos[1] = (intro.cursor_pos[1] + 1) % len(intro.skin_options)
        elif pressed_key == pygame.K_UP:
            intro.cursor_pos[1] = (intro.cursor_pos[1] - 1) % len(intro.skin_options)
        elif pressed_key == pygame.K_z or pressed_key == pygame.K_RETURN:
            chosen_skin = intro.skin_options[intro.cursor_pos[1]]
            intro.begin_confirmation("skin", chosen_skin)

    # Name entry
    elif intro.scene == 3:
        if pressed_key == pygame.K_BACKSPACE:
            intro.name_buffer = intro.name_buffer[:-1]
        elif pressed_key == pygame.K_RETURN:
            if intro.name_buffer.strip():
                intro.begin_confirmation("name", intro.name_buffer.strip())

    # Starter select
    elif intro.scene == 5:
        if pressed_key == pygame.K_DOWN:
            intro.cursor_pos[1] = (intro.cursor_pos[1] + 1) % len(intro.starter_options)
        elif pressed_key == pygame.K_UP:
            intro.cursor_pos[1] = (intro.cursor_pos[1] - 1) % len(intro.starter_options)
        elif pressed_key == pygame.K_z or pressed_key == pygame.K_RETURN:
            chosen_starter = intro.starter_options[intro.cursor_pos[1]]
            intro.begin_confirmation("starter", chosen_starter)
    return None, intro.player

def handle_text_input(event, intro):
    if intro.scene == 3 and not intro.awaiting_confirmation:
        if event.unicode.isalpha() and len(intro.name_buffer) < 12:
            intro.name_buffer += event.unicode


def advance_dialogue(intro):
    if intro.scene == 1:
        intro.dialogue_number += 1
        if intro.dialogue_number >= len(intro.intro_dialogue):
            intro.scene = 2
            intro.cursor_pos = [0, 0]
            intro.dialogue_number = 0

    elif intro.scene == 4:
        intro.dialogue_number += 1
        if intro.dialogue_number >= len(intro.starters_dialogue):
            intro.scene = 5
            intro.cursor_pos = [0, 0]
            intro.dialogue_number = 0

    elif intro.scene == 6:
        intro.dialogue_number += 1
        if intro.dialogue_number >= len(intro.conclusion_dialogue):
            return "overworld"
    return None


def draw_text(surface, text, x, y, color=(255, 255, 255), font=None):
    if font is None:
        font = pygame.font.SysFont(None, 32)
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_confirmation_box(surface, intro, gamefont_small, gamefont_tiny):
    if not intro.awaiting_confirmation or not intro.pending_choice:
        return

    _, value = intro.pending_choice

    box = pygame.Rect(120, 220, 400, 120)
    pygame.draw.rect(surface, (255, 255, 255), box, 2)

    draw_text(surface, f"{value}? Are you sure?", 140, 240, font=gamefont_small)
    yes_prefix = ">" if intro.confirm_cursor == 0 else " "
    no_prefix = ">" if intro.confirm_cursor == 1 else " "
    draw_text(surface, f"{yes_prefix} Yes", 160, 280, font=gamefont_small)
    draw_text(surface, f"{no_prefix} No", 260, 280, font=gamefont_small)


def draw_dialogue_box(surface, text, gamefont):
    box = pygame.Rect(20, 300, 460, 120)
    pygame.draw.rect(surface, (255, 255, 255), box, 2)
    draw_text(surface, text, 60, 330, font=gamefont)


def draw(game_surface, intro, gamefont, gamefont_small, gamefont_tiny):
    game_surface.fill((0, 0, 0))

    # Scene 0: continue/new game
    if intro.scene == 0:
        options = ["Continue", "New Game"]
        for i, option in enumerate(options):
            prefix = ">" if intro.cursor_pos[1] == i else " "
            draw_text(game_surface, f"{prefix} {option}", 240, 140 + i * 40, font=gamefont)

    # Scene 1: intro dialogue
    elif intro.scene == 1:
        draw_dialogue_box(game_surface, intro.intro_dialogue[intro.dialogue_number], gamefont_tiny)

    # Scene 2: skin choice
    elif intro.scene == 2:
        draw_dialogue_box(game_surface, "Choose your appearance.", gamefont_tiny)
        for i, option in enumerate(intro.skin_options):
            prefix = ">" if intro.cursor_pos[1] == i else " "
            draw_text(game_surface, f"{prefix} {option}", 220, 120 + i * 40, font=gamefont_small)

    # Scene 3: name input
    elif intro.scene == 3:
        draw_dialogue_box(game_surface, "What is your name?", gamefont_tiny)
        draw_text(game_surface, intro.name_buffer + "_", 200, 180, font=gamefont_small)

    # Scene 4: starter intro dialogue
    elif intro.scene == 4:
        text = intro.starters_dialogue[intro.dialogue_number]
        if intro.dialogue_number == 0 and intro.player_name:
            text = f"Pleased to meet you {intro.player_name}"
        draw_dialogue_box(game_surface, text, gamefont_tiny)

    # Scene 5: starter select
    elif intro.scene == 5:
        draw_dialogue_box(game_surface, "Choose your starter.", gamefont_tiny)
        for i, option in enumerate(intro.starter_options):
            prefix = ">" if intro.cursor_pos[1] == i else " "
            draw_text(game_surface, f"{prefix} {option}", 220, 120 + i * 40, font=gamefont_small)

    # Scene 6: conclusion
    elif intro.scene == 6:
        draw_dialogue_box(game_surface, intro.conclusion_dialogue[intro.dialogue_number], gamefont_tiny)

    draw_confirmation_box(game_surface, intro, gamefont_small, gamefont_tiny)