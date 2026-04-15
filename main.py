import sys
import pygame

import battlescript
import overworld
import intro
from classes import playerdata
from classes import gameflags

gameflags.clear_all_flags()


# ----------------------------
# CONFIG
# ----------------------------
BASE_WIDTH = 500
BASE_HEIGHT = 500
FPS = 60
WINDOW_TITLE = "Pokemon Orange"
FONT_PATH = "resources/font/munro.ttf"


def get_scaled_rect(window_size):
    """
    Return the largest rectangle with the game's aspect ratio
    that fits inside the current window.
    """
    window_width, window_height = window_size

    scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
    scaled_width = int(BASE_WIDTH * scale)
    scaled_height = int(BASE_HEIGHT * scale)

    offset_x = (window_width - scaled_width) // 2
    offset_y = (window_height - scaled_height) // 2

    return pygame.Rect(offset_x, offset_y, scaled_width, scaled_height)


def window_to_game_coords(mouse_pos, scaled_rect):
    """
    Convert a mouse position from window coordinates into
    internal game-surface coordinates.
    """
    mouse_x, mouse_y = mouse_pos

    if not scaled_rect.collidepoint(mouse_x, mouse_y):
        return None

    game_x = (mouse_x - scaled_rect.x) * BASE_WIDTH / scaled_rect.width
    game_y = (mouse_y - scaled_rect.y) * BASE_HEIGHT / scaled_rect.height

    return int(game_x), int(game_y)


def create_fonts():
    """Create the main fonts used by the game."""
    gamefont = pygame.font.Font(FONT_PATH, BASE_HEIGHT // 10)
    gamefont_small = pygame.font.Font(FONT_PATH, BASE_HEIGHT // 20)
    gamefont_tiny = pygame.font.Font(FONT_PATH, BASE_HEIGHT // 25)
    return gamefont, gamefont_small, gamefont_tiny


def start_overworld():
    """Create the starting overworld state."""
    return overworld.build_stage()


def start_battle_from_encounter(encounter, player):
    """
    Build a battle object from an encounter list.

    Expected format:
    ['wild', pokemon]
    or
    ['trainerid', pokemon1, pokemon2, ...]
    """
    encounter_type = encounter[0] if encounter[0] == 'wild' else 'trainer'
    enemy_party = [encounter[1]] if encounter_type == "wild" else encounter[1:]

    return battlescript.start_battle(
        playerdata.get_player_party(player),
        enemy_party,
        battlefield="default",
        weather=None,
        terrain=None,
        can_run=(encounter_type == "wild"),
        ai=encounter_type,
        enemy_id = None if encounter[0] == 'wild' else encounter[0]
    )


def main():
    pygame.init()

    window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()
    gamefont, gamefont_small, gamefont_tiny = create_fonts()

    gamestate = "intro"

    # Initial state objects
    player = playerdata.Player("", "", [], {})
    game_stage = start_overworld()
    battle = None
    introduction = intro.Introduction(0)

    running = True
    while running:
        clock.tick(FPS)
        window.fill((0, 0, 0))
        game_surface.fill((20, 20, 20))

        keys = pygame.key.get_pressed()
        pressed_key = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                scaled_rect = get_scaled_rect(window.get_size())
                game_mouse = window_to_game_coords(event.pos, scaled_rect)
                if game_mouse is not None:
                    print("Game-space mouse:", game_mouse)

            elif event.type == pygame.KEYDOWN:
                pressed_key = event.key

                if gamestate == 'intro':
                    intro.handle_text_input(event, introduction)
    

        if gamestate == "intro":
            new_gamestate, player = intro.check_action(pressed_key, introduction)

            if new_gamestate == "overworld":
                gamestate = "overworld"

                # optional, depending on how your player data works:
                # playerdata.player_name = introduction.player_name
                # playerdata.starter = introduction.player_starter

                game_stage = start_overworld()
            if new_gamestate == None:
                intro.draw(game_surface, introduction, gamefont, gamefont_small, gamefont_tiny)

        elif gamestate == "overworld":
            game_stage, movement, facing, offset, new_gamestate, encounter = overworld.check_action(
                keys,
                game_stage,
                FPS,
                BASE_WIDTH,
                BASE_HEIGHT,
                pressed_key,
                player,
            )

            if new_gamestate == "battle" and encounter is not None:
                gamestate = "battle"
                battle = start_battle_from_encounter(encounter, player)

            overworld.draw(
                game_stage,
                overworld.get_player_sprites(player),
                movement,
                facing,
                game_surface,
                offset,
                gamefont_tiny
            )

        elif gamestate == "battle":
            new_gamestate = battlescript.check_action(pressed_key, battle)
            if new_gamestate == "overworld":
                gamestate = "overworld"

            battlescript.draw(battle, game_surface, gamefont, gamefont_small)

        # Scale the fixed-resolution game surface into the resizable window.
        scaled_rect = get_scaled_rect(window.get_size())
        scaled_surface = pygame.transform.scale(
            game_surface,
            (scaled_rect.width, scaled_rect.height),
        )

        window.blit(scaled_surface, scaled_rect.topleft)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()