import random
import pygame

from classes import assets
from classes import gameflags

class Battle:
    """
    Holds all state for a single battle instance.
    """

    def __init__(
        self,
        player_party,
        enemy_party,
        battlefield="default",
        weather=None,
        terrain=None,
        can_run=True,
        ai="wild",
        enemy_id = None
    ):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.player_active_member = player_party[0]
        self.enemy_active_member = enemy_party[0]

        self.weather = weather
        self.terrain = terrain
        self.battlefield = battlefield
        self.can_run = can_run
        self.ai = ai
        self.enemy_id = enemy_id

        self.lock_controls = False
        self.cursor_position = (0, 0)
        self.menu_layer = "main"   # "main" or "move"
        self.selected_move = None

        self.player_fainted = False
        self.enemy_fainted = False

        # message is displayed to the player and cleared with Z
        if self.enemy_id == None:
            self.message = f"Wild {self.enemy_active_member.getname()} attacked!"
        else:
            self.message = f"{self.enemy_id} wants to battle"
        # used when a message should be acknowledged before changing state
        self.pending_gamestate = None

    def try_run(self):
        """
        Attempt to flee from battle.
        Returns 'overworld' on success, otherwise None.
        """
        if self.ai != "wild":
            print("Couldn't escape!")
            return None

        run_roll = random.randint(0, 255)
        run_threshold = (
            self.player_active_member.getspe() * 32
            / ((self.enemy_active_member.getspe() / 4) % 256)
        ) + 30

        if run_roll < run_threshold:
            print("Got away safely!")
            return "overworld"

        return None

    def select_enemy_move(self):
        """
        Choose the enemy's move.
        For now, all AI just picks randomly.
        """
        return random.choice(list(self.enemy_active_member.moves.values()))

    def _determine_turn_order(self, enemy_move):
        """
        Decide who acts first based on move priority, then speed, then coin flip.
        """
        player_priority = self.selected_move.priority
        enemy_priority = enemy_move.priority

        if player_priority > enemy_priority:
            return "player"
        if enemy_priority > player_priority:
            return "enemy"

        player_speed = self.player_active_member.getspe()
        enemy_speed = self.enemy_active_member.getspe()

        if player_speed > enemy_speed:
            return "player"
        if enemy_speed > player_speed:
            return "enemy"

        return random.choice(["player", "enemy"])

    def _append_effectiveness_message(self, move_result, messages):
        """
        Add effectiveness text from a move result.
        Assumes effectiveness multiplier is at index 2.
        """
        effectiveness = move_result[2]

        if effectiveness == 0:
            messages.append("It had no effect!")
        elif effectiveness < 1:
            messages.append("It's not very effective...")
        elif effectiveness > 1:
            messages.append("It's super effective!")

    def _execute_attack(self, attacker, defender, move, messages):
        """
        Execute one move and append any needed messages.

        Returns:
            move_result, defender_fainted
        """
        move_result = move.executemove(attacker, defender)
        self._append_effectiveness_message(move_result, messages)

        defender_fainted = move_result[0] == "hit" and defender.fainted
        if defender_fainted:
            messages.append(f"{defender.getname()} fainted!")

        return move_result, defender_fainted

    def _handle_player_turn_first(self, enemy_move, messages):
        """
        Resolve a turn where the player acts first.
        """
        _, enemy_fainted = self._execute_attack(
            self.player_active_member,
            self.enemy_active_member,
            self.selected_move,
            messages,
        )

        if enemy_fainted:
            self.enemy_fainted = True
            return

        _, player_fainted = self._execute_attack(
            self.enemy_active_member,
            self.player_active_member,
            enemy_move,
            messages,
        )

        if player_fainted:
            self.player_fainted = True

    def _handle_enemy_turn_first(self, enemy_move, messages):
        """
        Resolve a turn where the enemy acts first.
        """
        _, player_fainted = self._execute_attack(
            self.enemy_active_member,
            self.player_active_member,
            enemy_move,
            messages,
        )

        if player_fainted:
            self.player_fainted = True
            return

        _, enemy_fainted = self._execute_attack(
            self.player_active_member,
            self.enemy_active_member,
            self.selected_move,
            messages,
        )

        if enemy_fainted:
            self.enemy_fainted = True

    def _handle_post_turn(self, messages):
        """
        Handle fainting, experience, enemy switching, and battle-end messages.
        """
        if self.player_fainted:
            if can_party_continue(self.player_party):
                messages.append("Choose a new Pokemon to send out!")
            else:
                messages.append("Your party is out of Pokemon! Game over!")

        if self.enemy_fainted:
            exp_gain = (
                self.enemy_active_member.getbasestattotal()
                * self.enemy_active_member.level
            ) // 7
            self.player_active_member.addexperience(exp_gain)

            if can_party_continue(self.enemy_party):
                messages.append("Enemy is sending out a new Pokemon!")
                self.enemy_active_member = next(
                    member for member in self.enemy_party if not member.fainted
                )
                self.enemy_fainted = False
            else:
                messages.append("You defeated the enemy!")
                self.message = " ".join(messages)
                if self.enemy_id:
                    gameflags.defeat_trainer(self.enemy_id)
                self.pending_gamestate = "overworld"
                return None

        self.message = " ".join(messages)
        return None

    def advance_turn(self):
        """
        Advance the battle by one player action.
        """
        self.message = ""
        messages = []

        if self.selected_move is None:
            return None

        if self.selected_move == "run":
            if self.ai == "wild":
                if self.try_run():
                    return "overworld"
                # Failed run: enemy gets a free turn.
                enemy_move = self.select_enemy_move()
                _, player_fainted = self._execute_attack(
                    self.enemy_active_member,
                    self.player_active_member,
                    enemy_move,
                    messages,
                )
                if player_fainted:
                    self.player_fainted = True
            else:
                print("Can't run from trainer battles!")
                self.selected_move = None
                return None
        else:
            enemy_move = self.select_enemy_move()
            turn_order = self._determine_turn_order(enemy_move)

            if turn_order == "player":
                self._handle_player_turn_first(enemy_move, messages)
            else:
                self._handle_enemy_turn_first(enemy_move, messages)

        self.selected_move = None
        self.menu_layer = "main"

        return self._handle_post_turn(messages)


def can_party_continue(party):
    """
    Return True if at least one party member has not fainted.
    """
    for member in party:
        if not member.fainted:
            return True
    return False


def start_battle(
    player_party,
    enemy_party,
    battlefield="default",
    weather=None,
    terrain=None,
    can_run=True,
    ai="wild",
    enemy_id = None,
):
    return Battle(player_party, enemy_party, battlefield, weather, terrain, can_run, ai, enemy_id)


def _move_cursor(battle, pressed_key):
    """
    Move the 2x2 battle menu cursor.
    """
    x, y = battle.cursor_position

    if pressed_key == pygame.K_RIGHT:
        battle.cursor_position = ((x + 1) % 2, y)
    elif pressed_key == pygame.K_LEFT:
        battle.cursor_position = ((x - 1) % 2, y)
    elif pressed_key == pygame.K_DOWN:
        battle.cursor_position = (x, (y + 1) % 2)
    elif pressed_key == pygame.K_UP:
        battle.cursor_position = (x, (y - 1) % 2)


def _select_move_from_cursor(battle):
    """
    Convert the cursor position into the chosen move.
    """
    moves_list = list(battle.player_active_member.moves.values())
    x, y = battle.cursor_position
    index = y * 2 + x

    if 0 <= index < len(moves_list):
        battle.selected_move = moves_list[index]
    else:
        battle.selected_move = None


def _handle_confirm(battle):
    """
    Handle Z key input in the battle menu.
    """
    if battle.message != "":
        battle.message = ""
        if battle.pending_gamestate is not None:
            next_state = battle.pending_gamestate
            battle.pending_gamestate = None
            return next_state
        return None

    if battle.menu_layer == "main":
        if battle.cursor_position == (0, 0):
            battle.menu_layer = "move"
        elif battle.cursor_position == (1, 0):
            print("pokemon menu not implemented yet")
        elif battle.cursor_position == (0, 1):
            print("bag menu not implemented yet")
        elif battle.cursor_position == (1, 1):
            if battle.can_run:
                battle.selected_move = "run"

    elif battle.menu_layer == "move":
        _select_move_from_cursor(battle)

    return None


def check_action(pressed_key, battle):
    """
    Handle one battle input event.
    """
    if battle.lock_controls:
        return None

    if pressed_key in (pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP):
        _move_cursor(battle, pressed_key)

    elif pressed_key == pygame.K_z:
        new_gamestate = _handle_confirm(battle)
        if new_gamestate is not None:
            return new_gamestate

    if battle.selected_move is not None:
        return battle.advance_turn()

    return None


def _draw_battlefield(battle, game_surface):
    battlefield_image = assets.get_scaled_image(
        f"graphics/battlefields/{battle.battlefield}.png",
        (500, 500),
        )
    game_surface.blit(battlefield_image, (0, 0))


def _draw_pokemon_sprites(battle, game_surface):
    player_sprite = assets.get_scaled_image(battle.player_active_member.sprite, (100, 100))
    enemy_sprite = assets.get_scaled_image(battle.enemy_active_member.sprite, (100, 100))

    game_surface.blit(player_sprite, (70, 200))
    game_surface.blit(enemy_sprite, (310, 50))


def _draw_status_text(battle, game_surface, gamefont_small):
    game_surface.blit(
        gamefont_small.render(f"{battle.player_active_member.getname()}", True, (0, 0, 0)),
        (295, 215),
    )
    game_surface.blit(
        gamefont_small.render(
            f"HP: {battle.player_active_member.getcurrenthp()}/{battle.player_active_member.getmaxhp()}",
            True,
            (0, 0, 0),
        ),
        (295, 240),
    )
    game_surface.blit(
        gamefont_small.render(
            f"EXP: {battle.player_active_member.experience}/{battle.player_active_member.level ** 3}",
            True,
            (0, 0, 0),
        ),
        (295, 265),
    )
    game_surface.blit(
        gamefont_small.render(f"LV: {battle.player_active_member.level}", True, (0, 0, 0)),
        (295, 290),
    )

    game_surface.blit(
        gamefont_small.render(f"{battle.enemy_active_member.getname()}", True, (0, 0, 0)),
        (35, 35),
    )
    game_surface.blit(
        gamefont_small.render(
            f"HP: {battle.enemy_active_member.getcurrenthp()}/{battle.enemy_active_member.getmaxhp()}",
            True,
            (0, 0, 0),
        ),
        (35, 60),
    )
    game_surface.blit(
        gamefont_small.render(f"LV: {battle.enemy_active_member.level}", True, (0, 0, 0)),
        (35, 85),
    )


def _draw_message_box(battle, game_surface, gamefont):
    """
    Draw the current battle message split into fixed chunks.
    """
    game_surface.blit(gamefont.render(battle.message[:20], True, (0, 0, 0)), (20, 310))
    game_surface.blit(gamefont.render(battle.message[20:40], True, (0, 0, 0)), (20, 355))
    game_surface.blit(gamefont.render(battle.message[40:60], True, (0, 0, 0)), (20, 400))
    game_surface.blit(gamefont.render(battle.message[60:], True, (0, 0, 0)), (20, 445))


def _draw_cursor(game_surface, cursor_position):
    cursor = assets.get_scaled_image("graphics/ui/cursor.png", (50, 50))
    game_surface.blit(
        cursor,
        (5 + cursor_position[0] * 220, 345 + cursor_position[1] * 60),
    )


def _draw_main_menu(battle, game_surface, gamefont):
    options = ["Fight", "Pokemon", "Bag", "Run"]

    for i, option in enumerate(options):
        color = (50, 50, 50) if battle.cursor_position == (i % 2, i // 2) else (0, 0, 0)
        game_surface.blit(
            gamefont.render(option, True, color),
            (50 + (i % 2) * 220, 340 + (i // 2) * 60),
        )

    _draw_cursor(game_surface, battle.cursor_position)


def _draw_move_menu(battle, game_surface, gamefont):
    moves_list = list(battle.player_active_member.moves.values())

    for i, move in enumerate(moves_list):
        color = (50, 50, 50) if battle.cursor_position == (i % 2, i // 2) else (0, 0, 0)
        game_surface.blit(
            gamefont.render(move.name, True, color),
            (50 + (i % 2) * 220, 340 + (i // 2) * 60),
        )

    _draw_cursor(game_surface, battle.cursor_position)


def draw(battle, game_surface, gamefont, gamefont_small):
    """
    Draw the entire battle screen.
    """
    game_surface.fill((255, 0, 0))  # Red background for testing

    _draw_battlefield(battle, game_surface)
    _draw_pokemon_sprites(battle, game_surface)
    _draw_status_text(battle, game_surface, gamefont_small)

    if battle.message != "":
        _draw_message_box(battle, game_surface, gamefont)
    elif battle.menu_layer == "main":
        _draw_main_menu(battle, game_surface, gamefont)
    elif battle.menu_layer == "move":
        _draw_move_menu(battle, game_surface, gamefont)