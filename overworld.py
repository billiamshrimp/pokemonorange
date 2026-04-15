import random
import pygame

from classes import assets
from classes import eventscript
from classes import gameflags
from classes import playerdata
from classes import pokemon


# ---------------------------------------------------------------------------
# Overworld configuration
# ---------------------------------------------------------------------------

TILE_SIZE = 50

WALKABLE_TILES = {
    "0001", "0003", "0005", "0006", "0007", "0008",
    "0032", "0037", "0041", "0043", "0044", "0050",
    "0078", "0091", "0093", "0094", "0095", "0096",
    "0097", "0098", "0099", "0100", "0101", "0102",
    "0103", "0104", "0105", "0106", "0107", "0108",
    "0109", "0110", "0111", "0112", "0113", "0114",
    "0115", "0116", "0117", "0118", "0119", "0120",
    "0121", "0122", "0123", "0124", "0125", "0126",
    "0127", "0128", "0129", "0130", "0131", "0137",
    "0141", "0154", "0155", "0156", "0157", "0181",
    
}
GRASS_TILES = {"0003", "0067", "0068", "0069", "0070"}
WATER_TILES = {"0004", "0042", "0080", "0081", "0082", "0083",}

MENU_OPTIONS = [
    "Pokedex",
    "Pokemon",
    "Bag",
    "Card",
    "Save",
    "Option",
    "Exit",
]

OPPOSITE_FACING = {
    "north": "south",
    "south": "north",
    "west": "east",
    "east": "west",
}

PLAYER_DIRECTION_ABBREVIATIONS = {
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
}


# ---------------------------------------------------------------------------
# Core overworld data classes
# ---------------------------------------------------------------------------

class Stage:
    """
    Represents the current overworld map.

    A Stage owns:
    - map dimensions and tile data
    - raw map object data (trainers, items, NPCs)
    - runtime movement / dialogue / menu state
    - cached built object instances used during play
    """

    def __init__(self, width, height, objects, warps, connections, events, position, wild, inside, tiledata):
        self.width = width
        self.height = height
        self.objects = objects[0]
        self.warps = warps[0]
        self.connections = connections[0]
        self.events = events
        self.position = [int(position[0]), int(position[1])]
        self.wild = wild
        self.inside = inside
        self.tiledata = tiledata

        # Player movement state
        self.moving = False
        self.move_dir = (0, 0)
        self.move_progress = 0
        self.move_frames = 0
        self.speed_per_frame = 0
        self.facing = "south"
        self.movement = "1"

        # Interaction state
        self.interacting = False
        self.await_z_release = False

        # Pause menu state
        self.menu_selection = 0
        self.display_menu = False

        # Dialogue box state
        self.display_dialogue = False
        self.dialogue = ""

        # Active interactables
        self.active_trainer = None
        self.active_item = None
        self.active_npc = None

        # Raw object groupings
        self.trainers = []
        self.items = []
        self.npcs = []

        self.pending_connection = None

        # Built runtime objects
        self.built_trainers = []
        self.built_items = []
        self.built_npcs = []
        self._categorize_objects()

    def _categorize_objects(self):
        """Split raw map objects into convenient category lists."""
        for obj in self.objects:
            obj_type = obj[0]
            if obj_type == "trainer":
                self.trainers.append(obj)
            elif obj_type == "item":
                self.items.append(obj)
            elif obj_type == "npc":
                self.npcs.append(obj)

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x, y):
        """
        Return True if the player may step onto the target tile.

        A tile is walkable only if:
        - it is inside map bounds
        - the tile id is in WALKABLE_TILES
        - a trainer is not occupying it
        - an uncollected item is not occupying it
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        tile_is_walkable = self.tiledata[y][x] in WALKABLE_TILES

        occupied_by_trainer = any(
            trainer[1] == x and trainer[2] == y
            for trainer in self.trainers
        )

        occupied_by_npc = any(
            int(npc[1]) == x and int(npc[2]) == y
            for npc in self.npcs 
        )

        occupied_by_item = any(
            int(item[1]) == x
            and int(item[2]) == y
            and item[3][0] not in gameflags.get_collected_items()
            for item in self.items
        )

        return tile_is_walkable and not occupied_by_trainer and not occupied_by_item and not occupied_by_npc

    def is_swimable(self, x, y):
        """Return True if the tile is water and within bounds."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiledata[y][x] in WATER_TILES

    def try_warp(self):
        """
        Return (True, new_stage) if the player is standing on a warp tile.
        Otherwise return (False, None).
        """
        for warp in self.warps:
            if warp == 'none':
                continue

            warp_data = warp.split(",")
            warp_x, warp_y = warp_data[0], warp_data[1]
            destination_stage = warp_data[2]
            destination_coords = [int(coord) for coord in warp_data[3:5]]

            if warp_x == str(self.position[0]) and warp_y == str(self.position[1]):
                return True, build_stage(destination_stage, destination_coords)

        return False, None

    def try_connect(self, target_x, target_y):
        """
        Return (True, connection_data) if the attempted move leaves the map
        through a valid connected edge. Otherwise return (False, None).

        connection_data:
            {
                "stage": destination_stage,
                "coords": (new_x, new_y),
            }
        """
        for connection in self.connections:
            if connection == "none":
                continue

            direction, destination_stage, offset = connection.split(",")
            offset = int(offset)

            destination_width, destination_height = get_stage_dimensions(destination_stage)

            new_x = None
            new_y = None

            if direction == "north" and target_y < 0:
                new_x = self.position[0] - offset
                new_y = destination_height - 1

            elif direction == "south" and target_y >= self.height:
                new_x = self.position[0] - offset
                new_y = 0

            elif direction == "west" and target_x < 0:
                new_x = destination_width - 1
                new_y = self.position[1] - offset

            elif direction == "east" and target_x >= self.width:
                new_x = 0
                new_y = self.position[1] - offset

            else:
                continue

            if not (0 <= new_x < destination_width and 0 <= new_y < destination_height):
                print(
                    f"[WARN] Invalid connection from current map to {destination_stage} "
                    f"at ({new_x}, {new_y})"
                )
                return False, None

            return True, {
                "stage": destination_stage,
                "coords": (new_x, new_y),
            }

        return False, None

    def try_wild_encounter(self):
        """
        Return (True, [level, species]) if a wild encounter should begin.

        Current behavior:
        - only checks grass tiles
        - uses a 1-in-13 roll
        - pulls a random species and random level from this map's wild data
        """
        if self.tiledata[self.position[1]][self.position[0]] not in GRASS_TILES:
            return False, None

        if random.randint(0, 12) != 0:
            return False, None

        wild_data = self.wild[0][0].split(",")
        min_level = int(wild_data[1])
        max_level = int(wild_data[2])
        species_list = wild_data[3].split(".")

        species = int(random.choice(species_list))
        level = random.randint(min_level, max_level)
        return True, [level, species]


class Trainer:
    """Runtime trainer object used for drawing, approach movement, and battle setup."""

    def __init__(self, name, sprite_name, party, facing, position, defeated=False):
        self.name = name
        self.sprite_name = sprite_name
        self.party = party
        self.facing = facing
        self.position = position
        self.defeated = defeated

        # Movement / animation state
        self.moving = False
        self.move_dir = (0, 0)
        self.move_progress = 0
        self.move_frames = 0
        self.speed_per_frame = 0
        self.movement = "1"
        self.approach_steps = 0

        # Sprite caching
        self.sprite_cache = {}
        self.sprite = None
        self.refresh_sprite()

    def refresh_sprite(self):
        """Load or reuse the correct trainer sprite for current facing + frame."""
        sprite_key = (self.facing, self.movement)
        if sprite_key not in self.sprite_cache:
            sprite_path = (
                f"graphics/sprites/npc/{self.sprite_name}_{self.facing}_{self.movement}.png"
            )
            self.sprite_cache[sprite_key] = assets.get_scaled_image(
                sprite_path,
                (TILE_SIZE, TILE_SIZE),
            )
        self.sprite = self.sprite_cache[sprite_key]

    def try_encounter(self, player_position):
        """
        Return the number of tiles between trainer and player if spotted.

        Trainers currently see up to 3 tiles in the direction they face.
        Returns 0 if they do not spot the player.
        """
        if self.defeated:
            return 0

        delta_x = player_position[0] - self.position[0]
        delta_y = player_position[1] - self.position[1]

        if self.facing == "east" and delta_y == 0 and 1 <= delta_x <= 3:
            return delta_x
        if self.facing == "west" and delta_y == 0 and -3 <= delta_x <= -1:
            return -delta_x
        if self.facing == "south" and delta_x == 0 and 1 <= delta_y <= 3:
            return delta_y
        if self.facing == "north" and delta_x == 0 and -3 <= delta_y <= -1:
            return -delta_y

        return 0


class Item:
    """Runtime item object used for drawing and collection tracking."""

    def __init__(self, item_id, item_content, position, collected=False):
        self.item_id = item_id
        self.item_content = item_content
        self.position = position
        self.collected = collected
        self.sprite_path = "graphics/sprites/other/item.png"
        self.sprite = assets.get_scaled_image(self.sprite_path, (TILE_SIZE, TILE_SIZE))


class Npc:

    def __init__(self, npc_id, sprite_name, item_gift, facing, position, interacted=False):
        self.npc_id = npc_id
        self.sprite_name = sprite_name
        self.item_gift = item_gift
        self.facing = facing
        self.position = position
        self.interacted = interacted

        self.movement = '1'

        self.sprite_cache = {}
        self.sprite = None
        self.refresh_sprite()

    def refresh_sprite(self):
        sprite_key = (self.facing, self.movement)
        if sprite_key not in self.sprite_cache:
            sprite_path = (
                f"graphics/sprites/npc/{self.sprite_name}_{self.facing}_{self.movement}.png"
            )
            self.sprite_cache[sprite_key] = assets.get_scaled_image(
                sprite_path,
                (TILE_SIZE, TILE_SIZE),
            )
        self.sprite = self.sprite_cache[sprite_key]

# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def get_offset(screen_width, screen_height, game_map):
    """
    Return the map draw offset that keeps the player centered on screen.
    """
    offset_x = screen_width // 2 - game_map.position[0] * TILE_SIZE - TILE_SIZE // 2
    offset_y = screen_height // 2 - game_map.position[1] * TILE_SIZE - TILE_SIZE // 2
    return [offset_x, offset_y]


def get_player_sprites(player):
    """Build and return the player's overworld sprite set."""
    return playerdata.build_overworld_skin(player, TILE_SIZE)


def _is_adjacent_in_facing_direction(game_map, target_x, target_y):
    """
    Return True if the target coordinates are directly in front of the player.
    """
    player_x, player_y = game_map.position

    if game_map.facing == "north":
        return target_x == player_x and target_y == player_y - 1
    if game_map.facing == "south":
        return target_x == player_x and target_y == player_y + 1
    if game_map.facing == "west":
        return target_x == player_x - 1 and target_y == player_y
    if game_map.facing == "east":
        return target_x == player_x + 1 and target_y == player_y

    return False

def get_stage_dimensions(stageid):
    with open(f"resources/maps/{stageid}.map") as file:
        lines = file.read().splitlines()

    height = len(lines) - 7
    width = len(lines[7].split(","))

    return width, height

def _get_built_trainer_by_name(game_map, trainer_name):
    """Return a built trainer by name if already cached, else None."""
    return next((trainer for trainer in game_map.built_trainers if trainer.name == trainer_name), None)


def _get_built_item_by_id(game_map, item_id):
    """Return a built item by id if already cached, else None."""
    return next((item for item in game_map.built_items if item.item_id == item_id), None)


def _get_built_npc_by_id(game_map, npc_id):
    return next((npc for npc in game_map.built_npcs if npc.npc_id == npc_id), None)

# ---------------------------------------------------------------------------
# Build / parse helpers
# ---------------------------------------------------------------------------

def build_trainer(trainer_data, facing="default"):
    """
    Convert parsed trainer map data into a Trainer object.
    """
    name = trainer_data[3][2]

    if facing == "default":
        facing = trainer_data[3][0]

    position = [int(trainer_data[1]), int(trainer_data[2])]
    sprite_name = trainer_data[3][1]
    defeated = name in gameflags.get_defeated_trainers()

    party = []
    for mon_data in trainer_data[3][3:]:
        species_id = int(mon_data[0])
        level = int(mon_data[1])
        party.append(pokemon.Pokemon(species_id, level))

    return Trainer(name, sprite_name, party, facing, position, defeated)


def build_item(item_data):
    """
    Convert parsed item map data into an Item object.
    """
    item_id = item_data[3][0]
    position = [int(item_data[1]), int(item_data[2])]
    collected = item_id in gameflags.get_collected_items()
    content = item_data[3][1]
    return Item(item_id, content, position, collected)


def build_npc(npc_data, facing='default'):
    npc_type = npc_data[3][1]
    position = [int(npc_data[1]), int(npc_data[2])]
    interacted = False # Placeholder
    npc_name = npc_data[3][2]
    if facing == 'default':
        npc_facing = npc_data[3][0]
    else:
        npc_facing = facing
    npc_item = npc_data[3][3]
    return Npc(npc_name, npc_type, npc_item, npc_facing, position, interacted)


def parse_object_data(raw_objects):
    """
    Parse object strings from the map file into structured lists.

    Trainer data is converted from a string layout into:
    [
        "trainer",
        x,
        y,
        [facing, sprite_name, trainer_name, [species, level], ...]
    ]
    """
    parsed_objects = []

    for group in raw_objects:
        parsed_group = []

        for obj in group:
            parts = obj.split(",")

            if parts[0] == "trainer":
                parts[1] = int(parts[1])
                parts[2] = int(parts[2])
                parts[3] = parts[3].split(".")

                for i in range(3, len(parts[3])):
                    mon_data = parts[3][i].split("-")
                    mon_data[0] = int(mon_data[0])
                    mon_data[1] = int(mon_data[1])
                    parts[3][i] = mon_data
            elif parts[0] == 'npc':
                parts[3] = parts[3].split(".")
            elif parts[0] == 'item':
                parts[3] = parts[3].split('.')

            parsed_group.append(parts)

        parsed_objects.append(parsed_group)

    return parsed_objects


def build_stage(stageid="player_room", coords=(2, 2)):
    """
    Load a .map file and return a fully built Stage object.
    """
    with open(f"resources/maps/{stageid}.map") as file:
        lines = file.read().splitlines()

    height = len(lines) - 7
    width = len(lines[7].split(","))

    objects = []
    warps = []
    connections = []
    wild = []
    tiledata = []

    inside = lines[0].strip().split(":")[1] == "true"

    for i in range(1, 6):
        key, value = lines[i].strip().split(":")

        if key == "wild":
            wild.append(value.split("|"))
        elif key == "warps":
            warps.append(value.split("|"))
        elif key == "connections":
            connections.append(value.split("|"))
        elif key == "objects":
            objects.append(value.split("|"))

    for row_index in range(height):
        row = lines[row_index + 7].split(",")
        tiledata.append(row)

    events = eventscript.get_events_for_stage(stageid)
    parsed_objects = parse_object_data(objects)
    new_x, new_y = coords

    if new_x == "rightmost":
        new_x = width - 1
    if new_y == "bottom":
        new_y = height - 1

    new_coords = (new_x, new_y)


    return Stage(
        width=width,
        height=height,
        objects=parsed_objects,
        warps=warps,
        connections=connections,
        events=events,
        position=list(new_coords),
        wild=wild,
        inside=inside,
        tiledata=tiledata,
    )

def load_stage_tiledata(stageid):
    with open(f"resources/maps/{stageid}.map") as file:
        lines = file.read().splitlines()

    height = len(lines) - 7
    width = len(lines[7].split(","))

    tiledata = []
    for row_index in range(height):
        row = lines[row_index + 7].split(",")
        tiledata.append(row)

    return width, height, tiledata


# ---------------------------------------------------------------------------
# Player movement helpers
# ---------------------------------------------------------------------------

def _start_move(game_map, keys, fps):
    """
    Attempt to begin a player movement step from held directional input.

    Returns:
        started_move, game_map
    """
    move_duration_base = 0.25
    speed_multiplier = 2

    dir_x, dir_y = 0, 0

    if keys[pygame.K_UP]:
        dir_y = -1
        game_map.facing = "north"
    elif keys[pygame.K_DOWN]:
        dir_y = 1
        game_map.facing = "south"
    elif keys[pygame.K_LEFT]:
        dir_x = -1
        game_map.facing = "west"
    elif keys[pygame.K_RIGHT]:
        dir_x = 1
        game_map.facing = "east"

    if dir_x == 0 and dir_y == 0:
        game_map.movement = "1"
        return False, game_map

    target_x = game_map.position[0] + dir_x
    target_y = game_map.position[1] + dir_y

        # Edge transition: allow the move only if a valid connection exists.
    if not game_map.in_bounds(target_x, target_y):
        need_to_connect, connection_data = game_map.try_connect(target_x, target_y)
        if not need_to_connect:
            return False, game_map

        game_map.pending_connection = connection_data

    else:
    # Normal in-bounds collision
        if not game_map.is_walkable(target_x, target_y):
            return False, game_map
        game_map.pending_connection = None

    is_fast = keys[pygame.K_x]
    duration = move_duration_base / speed_multiplier if is_fast else move_duration_base

    game_map.moving = True
    game_map.move_dir = (dir_x, dir_y)
    game_map.move_progress = 0
    game_map.move_frames = max(1, int(duration * fps))
    game_map.speed_per_frame = TILE_SIZE / game_map.move_frames
    return True, game_map


def _update_move_animation(game_map, base_width, base_height):
    """
    Advance player movement animation by one frame and return the draw offset.
    """
    dx = -game_map.move_dir[0] * game_map.speed_per_frame * game_map.move_progress
    dy = -game_map.move_dir[1] * game_map.speed_per_frame * game_map.move_progress

    offset = get_offset(base_width, base_height, game_map)
    offset[0] += dx
    offset[1] += dy

    game_map.move_progress += 1
    progress_ratio = game_map.move_progress / game_map.move_frames

    if progress_ratio >= 0.75:
        game_map.movement = "3"
    elif progress_ratio >= 0.25:
        game_map.movement = "2" if progress_ratio < 0.50 else "1"
    else:
        game_map.movement = "1"
    
        # If the completed step moved the player out of bounds, transition now.
    if not game_map.in_bounds(game_map.position[0], game_map.position[1]):
        need_to_connect, new_stage = game_map.try_connect(
            game_map.position[0],
            game_map.position[1]
        )
        if need_to_connect:
            game_map = new_stage
            offset = get_offset(base_width, base_height, game_map)
            return game_map, offset, None, None

    return offset


def _finish_move(game_map, base_width, base_height, fps):
    new_gamestate = None
    encounter = None

    game_map.moving = False
    game_map.move_progress = 0
    game_map.movement = "1"

    # Handle edge-map transition before applying an out-of-bounds position.
    if game_map.pending_connection is not None:
        destination_stage = game_map.pending_connection["stage"]
        destination_coords = game_map.pending_connection["coords"]

        game_map = build_stage(destination_stage, destination_coords)
        offset = get_offset(base_width, base_height, game_map)
        return game_map, offset, None, None

    # Normal in-bounds step
    game_map.position[0] += game_map.move_dir[0]
    game_map.position[1] += game_map.move_dir[1]

    offset = get_offset(base_width, base_height, game_map)

    # Wild encounter check
    found_wild, wild_data = game_map.try_wild_encounter()
    if found_wild:
        new_gamestate = "battle"
        encounter = ["wild", pokemon.Pokemon(wild_data[0], wild_data[1])]

    # Trainer sightline check
    for trainer_data in game_map.trainers:
        trainer_name = trainer_data[3][2]
        trainer = _get_built_trainer_by_name(game_map, trainer_name)

        if trainer is None:
            trainer = build_trainer(trainer_data)
            game_map.built_trainers.append(trainer)

        trainer.defeated = trainer.name in gameflags.get_defeated_trainers()

        trainer_encounter = trainer.try_encounter(game_map.position)
        if trainer_encounter:
            game_map.active_trainer = trainer
            game_map.interacting = True

            if trainer_encounter > 1:
                _start_trainer_approach(trainer, trainer_encounter - 1, fps)
            else:
                _get_and_show_dialogue(game_map, trainer, 'trainer')
            break

    # Warp check
    need_to_warp, new_stage = game_map.try_warp()
    if need_to_warp:
        game_map = new_stage
        offset = get_offset(base_width, base_height, game_map)

    return game_map, offset, new_gamestate, encounter


# ---------------------------------------------------------------------------
# Trainer movement helpers
# ---------------------------------------------------------------------------

def _start_trainer_approach(trainer, steps, fps):
    """
    Begin trainer auto-walking toward the player for the given number of steps.
    """
    if steps <= 0:
        return

    move_duration_base = 0.25

    trainer.approach_steps = steps - 1
    trainer.moving = True
    trainer.move_progress = 0
    trainer.move_frames = max(1, int(move_duration_base * fps))
    trainer.speed_per_frame = TILE_SIZE / trainer.move_frames
    trainer.movement = "1"

    if trainer.facing == "east":
        trainer.move_dir = (1, 0)
    elif trainer.facing == "west":
        trainer.move_dir = (-1, 0)
    elif trainer.facing == "south":
        trainer.move_dir = (0, 1)
    else:
        trainer.move_dir = (0, -1)

    trainer.refresh_sprite()


def _update_trainer_animation(trainer):
    """
    Advance trainer approach animation by one frame.
    """
    trainer.move_progress += 1
    progress_ratio = trainer.move_progress / trainer.move_frames

    if progress_ratio >= 0.75:
        trainer.movement = "3"
    elif progress_ratio >= 0.25:
        trainer.movement = "2" if progress_ratio < 0.50 else "1"
    else:
        trainer.movement = "1"

    trainer.refresh_sprite()


def _finish_trainer_approach(game_map, trainer, fps):
    """
    Complete one trainer approach step and either continue walking or show dialogue.
    """
    trainer.moving = False
    trainer.position[0] += trainer.move_dir[0]
    trainer.position[1] += trainer.move_dir[1]
    trainer.move_progress = 0
    trainer.movement = "1"
    trainer.refresh_sprite()

    # Also update the raw trainer data so collision / map state stay in sync.
    for trainer_data in game_map.trainers:
        if trainer_data[3][2] == trainer.name:
            trainer_data[1] = trainer.position[0]
            trainer_data[2] = trainer.position[1]
            break

    if trainer.approach_steps > 0:
        _start_trainer_approach(trainer, trainer.approach_steps, fps)
        return

    _get_and_show_dialogue(game_map, trainer, 'trainer')


# ---------------------------------------------------------------------------
# Dialogue / interaction helpers
# ---------------------------------------------------------------------------

def _get_and_show_dialogue(game_map, interactee, interaction_type):
    """
    Populate the dialogue box and open it.

    trainer may be:
    - a Trainer/npc object
    - the string 'item' for item pickup text
    """
    if interaction_type == "item":
        game_map.dialogue = f"You collected {interactee.item_content}"
    elif interaction_type == 'trainer':
        dialogue_index = 0 if not interactee.defeated else 1
        game_map.dialogue = eventscript.get_dialogue_for_npc(interactee.name, dialogue_index)
    elif interaction_type == 'npc':
        dialogue_index = 0 if not interactee.interacted else 1
        game_map.dialogue = eventscript.get_dialogue_for_npc(interactee.npc_id, dialogue_index)

    game_map.display_dialogue = True
    game_map.interacting = True
    game_map.await_z_release = True


def _advance_trainer_dialogue(game_map, pressed_key):
    """
    Advance trainer dialogue on a fresh Z press.

    If the trainer has not yet been defeated, this closes dialogue and starts battle.
    Returns:
        (new_gamestate, encounter) or (None, None)
    """
    if game_map.active_trainer is None:
        return None, None

    if pressed_key == pygame.K_z and not game_map.await_z_release:
        game_map.display_dialogue = False
        game_map.interacting = False

        trainer = game_map.active_trainer
        game_map.active_trainer = None
        trainer.defeated = trainer.name in gameflags.get_defeated_trainers()

        if trainer.defeated:
            return None, None

        return "battle", [trainer.name, *trainer.party]

    return None, None


def _advance_item_dialogue(game_map, pressed_key, player):
    """
    Advance item dialogue on a fresh Z press and mark the item collected.
    """
    if game_map.active_item is None:
        return

    if pressed_key == pygame.K_z and not game_map.await_z_release:
        game_map.display_dialogue = False
        game_map.interacting = False

        item = game_map.active_item
        game_map.active_item = None
        item.collected = True
        player.add_item(item.item_content)
        gameflags.collect_item(item.item_id)


def _advance_npc_dialogue(game_map, pressed_key, player):
    if game_map.active_npc is None:
        return
    
    if pressed_key == pygame.K_z and not game_map.await_z_release:
        game_map.display_dialogue = False
        game_map.interacting = False

        npc = game_map.active_npc
        game_map.active_npc = None
        if not npc.interacted:
            npc.interacted = True
            if npc.item_gift is not None:
                player.add_item(npc.item_gift)
        


def _try_interact(game_map, pressed_key):
    """
    Attempt to interact with the tile directly in front of the player.

    Currently supports:
    - trainers
    - items
    """
    if pressed_key != pygame.K_z:
        return None

    for obj in game_map.objects:
        if obj[0] == 'none':
            continue

        obj_type = obj[0]
        obj_x = int(obj[1])
        obj_y = int(obj[2])

        if not _is_adjacent_in_facing_direction(game_map, obj_x, obj_y):
            continue

        if obj_type == "trainer":
            game_map.interacting = True
            trainer_name = obj[3][2]

            # Rebuild the interacted trainer so its facing updates immediately.
            existing_trainer = _get_built_trainer_by_name(game_map, trainer_name)
            if existing_trainer is not None:
                game_map.built_trainers = [
                    trainer for trainer in game_map.built_trainers
                    if trainer.name != trainer_name
                ]

            trainer = build_trainer(obj, OPPOSITE_FACING[game_map.facing])
            game_map.built_trainers.append(trainer)
            game_map.active_trainer = trainer
            _get_and_show_dialogue(game_map, trainer, 'trainer')
            return

        if obj_type == "item":
            item_id = obj[3][0]
            item = _get_built_item_by_id(game_map, item_id)

            if item is None:
                item = build_item(obj)
                game_map.built_items.append(item)

            if not item.collected:
                game_map.active_item = item
                _get_and_show_dialogue(game_map, item, 'item')

            return

        if obj_type == 'npc':
            npc_id = obj[3][2]
            existing_npc = _get_built_npc_by_id(game_map, npc_id)

            if existing_npc is not None:
                game_map.built_npcs = [
                    npc for npc in game_map.built_npcs
                    if npc.npc_id != npc_id
                ]

            npc = build_npc(obj, OPPOSITE_FACING[game_map.facing])
            game_map.built_npcs.append(npc)
            game_map.active_npc = npc
            _get_and_show_dialogue(game_map, npc, 'npc')

# ---------------------------------------------------------------------------
# Pause menu helpers
# ---------------------------------------------------------------------------

def _try_pause_menu(game_map, pressed_key):
    """
    Open or close the overworld pause menu on Enter.
    """
    if pressed_key == pygame.K_RETURN and not game_map.interacting and not game_map.display_menu:
        game_map.interacting = True
        game_map.display_menu = True
        game_map.menu_selection = 0
    elif pressed_key == pygame.K_RETURN and game_map.interacting and game_map.display_menu:
        game_map.display_menu = False


def _navigate_menu(game_map, pressed_key):
    """
    Handle pause menu movement and selection.
    """
    if pressed_key == pygame.K_DOWN:
        game_map.menu_selection = (game_map.menu_selection + 1) % len(MENU_OPTIONS)

    elif pressed_key == pygame.K_UP:
        game_map.menu_selection = (game_map.menu_selection - 1) % len(MENU_OPTIONS)

    elif pressed_key == pygame.K_z:
        selected_option = MENU_OPTIONS[game_map.menu_selection]

        if selected_option == "Exit":
            game_map.interacting = False
            game_map.display_menu = False
        else:
            print(selected_option)

    elif pressed_key in (pygame.K_x, pygame.K_ESCAPE):
        game_map.interacting = False
        game_map.display_menu = False


# ---------------------------------------------------------------------------
# Main overworld update
# ---------------------------------------------------------------------------

def check_action(keys, game_map, fps, base_width, base_height, pressed_key, player):
    """
    Update the overworld state for one frame.

    Returns:
        game_map, movement, facing, offset, new_gamestate, encounter
    """
    started_move = None
    new_gamestate = None
    encounter = None
    offset = get_offset(base_width, base_height, game_map)

    # Prevent held Z from instantly skipping fresh dialogue.
    if game_map.await_z_release and not keys[pygame.K_z]:
        game_map.await_z_release = False

    # Normal player input only works while not moving or locked in interaction.
    if not game_map.moving and not game_map.interacting:
        started_move, game_map = _start_move(game_map, keys, fps)

    # Also prevent new interactions while already interacting.
    if not started_move and not game_map.interacting:
        _try_interact(game_map, pressed_key)
        _try_pause_menu(game_map, pressed_key)

    # Animate player movement if already moving.
    if game_map.moving:
        offset = _update_move_animation(game_map, base_width, base_height)

        if game_map.move_progress >= game_map.move_frames:
            game_map, offset, new_gamestate, encounter = _finish_move(
                game_map,
                base_width,
                base_height,
                fps,
            )

    # Animate trainer walking toward the player, if applicable.
    if game_map.active_trainer is not None and game_map.active_trainer.moving:
        _update_trainer_animation(game_map.active_trainer)

        if game_map.active_trainer.move_progress >= game_map.active_trainer.move_frames:
            _finish_trainer_approach(game_map, game_map.active_trainer, fps)

    # Pause menu input
    if game_map.interacting and game_map.display_menu:
        _navigate_menu(game_map, pressed_key)

    # Dialogue input
    if game_map.interacting and game_map.display_dialogue:
        new_gamestate, encounter = _advance_trainer_dialogue(game_map, pressed_key)
        _advance_item_dialogue(game_map, pressed_key, player)
        _advance_npc_dialogue(game_map, pressed_key, player)

    return game_map, game_map.movement, game_map.facing, offset, new_gamestate, encounter


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _draw_tilemap(game_surface, tiledata, width, height, origin_x, origin_y):
    for y in range(height):
        for x in range(width):
            tile_id = tiledata[y][x]
            tile_image = assets.get_scaled_image(
                f"graphics/tiles/{tile_id}.png",
                (TILE_SIZE, TILE_SIZE),
                convert_alpha=False,
            )
            screen_x = origin_x + x * TILE_SIZE
            screen_y = origin_y + y * TILE_SIZE
            game_surface.blit(tile_image, (screen_x, screen_y))

def _draw_connected_maps(game_map, game_surface, offset):
    current_origin_x = offset[0]
    current_origin_y = offset[1]

    for connection in game_map.connections:
        if connection == "none":
            continue

        direction, destination_stage, offset_value = connection.split(",")
        offset_value = int(offset_value)

        neighbor_width, neighbor_height, neighbor_tiledata = load_stage_tiledata(destination_stage)

        if direction == "north":
            neighbor_origin_x = current_origin_x + offset_value * TILE_SIZE
            neighbor_origin_y = current_origin_y - neighbor_height * TILE_SIZE

        elif direction == "south":
            neighbor_origin_x = current_origin_x + offset_value * TILE_SIZE
            neighbor_origin_y = current_origin_y + game_map.height * TILE_SIZE

        elif direction == "west":
            neighbor_origin_x = current_origin_x - neighbor_width * TILE_SIZE
            neighbor_origin_y = current_origin_y + offset_value * TILE_SIZE

        elif direction == "east":
            neighbor_origin_x = current_origin_x + game_map.width * TILE_SIZE
            neighbor_origin_y = current_origin_y + offset_value * TILE_SIZE

        else:
            continue

        _draw_tilemap(
            game_surface,
            neighbor_tiledata,
            neighbor_width,
            neighbor_height,
            neighbor_origin_x,
            neighbor_origin_y,
        )

def draw(game_map, player_sprites, movement_progress, facing_direction, game_surface, offset, gamefont_tiny):
    """
    Draw the entire overworld frame:
    - map tiles
    - player
    - trainers / items
    - pause menu
    - dialogue box
    """
    # Draw connected neighboring maps first
    _draw_connected_maps(game_map, game_surface, offset)

    # Draw current map
    _draw_tilemap(
        game_surface,
        game_map.tiledata,
        game_map.width,
        game_map.height,
        offset[0],
        offset[1],
    )

    # Draw player centered on the screen
    direction_abbrev = PLAYER_DIRECTION_ABBREVIATIONS.get(facing_direction, "s")
    player_sprite_key = f"{direction_abbrev}_{movement_progress}"
    player_sprite = player_sprites.get(player_sprite_key)

    if player_sprite:
        player_screen_x = game_surface.get_width() // 2 - TILE_SIZE // 2
        player_screen_y = game_surface.get_height() // 2 - TILE_SIZE // 2
        game_surface.blit(player_sprite, (player_screen_x, player_screen_y))

    # Draw overworld objects
    for obj in game_map.objects:
        obj_type = obj[0]

        if obj_type == "trainer":
            trainer_name = obj[3][2]
            trainer = _get_built_trainer_by_name(game_map, trainer_name)

            # Build once on demand so later drawing can reflect runtime changes,
            # such as facing direction after interaction.
            if trainer is None:
                trainer = build_trainer(obj)
                game_map.built_trainers.append(trainer)

            trainer_screen_x = trainer.position[0] * TILE_SIZE + offset[0]
            trainer_screen_y = trainer.position[1] * TILE_SIZE + offset[1]

            if trainer.moving:
                trainer_screen_x += trainer.move_dir[0] * trainer.speed_per_frame * trainer.move_progress
                trainer_screen_y += trainer.move_dir[1] * trainer.speed_per_frame * trainer.move_progress

            game_surface.blit(trainer.sprite, (trainer_screen_x, trainer_screen_y))

        elif obj_type == "item":
            item_id = obj[3][0]
            item = _get_built_item_by_id(game_map, item_id)

            if item is None:
                item = build_item(obj)
                game_map.built_items.append(item)

            if not item.collected:
                item_screen_x = item.position[0] * TILE_SIZE + offset[0]
                item_screen_y = item.position[1] * TILE_SIZE + offset[1]
                game_surface.blit(item.sprite, (item_screen_x, item_screen_y))

        elif obj_type == "npc":
            npc_id = obj[3][2]
            npc = _get_built_npc_by_id(game_map, npc_id)

            if npc is None:
                npc = build_npc(obj)
                game_map.built_npcs.append(npc)
            
            npc_screen_x = npc.position[0] * TILE_SIZE + offset[0]
            npc_screen_y = npc.position[1] * TILE_SIZE + offset[1]
            game_surface.blit(npc.sprite, (npc_screen_x, npc_screen_y))

    # Draw pause menu
    if game_map.display_menu:
        pygame.draw.rect(game_surface, (220, 220, 220), (300, 50, 175, 400))
        pygame.draw.rect(game_surface, (180, 180, 180), (300, 50, 175, 400), width=4)

        cursor = pygame.transform.scale(
            pygame.image.load("graphics/ui/cursor.png").convert_alpha(),
            (30, 30),
        )
        game_surface.blit(cursor, (305, 55 + game_map.menu_selection * 60))

        for index, option in enumerate(MENU_OPTIONS):
            text_y = 55 + index * 60
            game_surface.blit(
                gamefont_tiny.render(option, True, (0, 0, 0)),
                (350, text_y),
            )

    # Draw dialogue box
    if game_map.display_dialogue:
        pygame.draw.rect(game_surface, (220, 220, 220), (50, 300, 400, 175))
        pygame.draw.rect(game_surface, (180, 180, 180), (50, 300, 400, 175), width=4)

        # Very simple two-line split for now.
        line_1 = game_map.dialogue[:45].strip(" ")
        line_2 = game_map.dialogue[45:].strip(" ")

        game_surface.blit(gamefont_tiny.render(line_1, True, (0, 0, 0)), (60, 310))
        game_surface.blit(gamefont_tiny.render(line_2, True, (0, 0, 0)), (60, 330))
