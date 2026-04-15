import os
import sys
import pygame


# =========================
# CONFIG
# =========================
TILE_SIZE = 32
PALETTE_TILE_SIZE = 32
PALETTE_COLUMNS = 3
PALETTE_PADDING = 8
SIDEBAR_WIDTH = 220
FPS = 60

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

MAX_WINDOW_WIDTH = 1400
MAX_WINDOW_HEIGHT = 900

MAP_FILE = "resources/maps/player_room.map"
TILE_FOLDER = "graphics/tiles"   # expects files like 0001.png, 0002.png, etc.


# =========================
# MAP LOADING / SAVING
# =========================
def load_map(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    map_data = {
        "inside": False,
        "objects": [],
        "warps": [],
        "connections": [],
        "wild": None,
        "conditions": [],
        "tiles": []
    }

    reading_tiles = False

    for line in lines:
        if not line:
            continue

        if reading_tiles:
            row = [cell.strip() for cell in line.split(",")]
            map_data["tiles"].append(row)
            continue

        if line == "configuration:":
            reading_tiles = True
            continue

        key, value = line.split(":", 1)

        if key == "inside":
            map_data["inside"] = value.lower() == "true"

        elif key == "objects":
            if value and value.lower() != "none":
                entries = value.split("|")
                for entry in entries:
                    parts = entry.split(",", 3)
                    if len(parts) < 3:
                        continue

                    obj = {
                        "type": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "data": parts[3] if len(parts) > 3 else ""
                    }
                    map_data["objects"].append(obj)

        elif key == "warps":
            if value and value.lower() != "none":
                entries = value.split("|")
                for entry in entries:
                    parts = entry.split(",")
                    if len(parts) != 5:
                        continue

                    warp = {
                        "x": int(parts[0]),
                        "y": int(parts[1]),
                        "target_map": parts[2],
                        "target_x": int(parts[3]),
                        "target_y": int(parts[4])
                    }
                    map_data["warps"].append(warp)

        elif key == "connections":
            if value and value.lower() != "none":
                entries = value.split("|")
                for entry in entries:
                    parts = entry.split(",")
                    if len(parts) != 3:
                        continue

                    connection = {
                        "direction": parts[0],
                        "destination": parts[1],
                        "offset": parts[2]
                    }
                    map_data["connections"].append(connection)

        elif key == "wild":
            if value and value.lower() != "none":
                parts = value.split(",")
                if len(parts) == 4:
                    map_data["wild"] = {
                        "terrain": parts[0],
                        "rate": int(parts[1]),
                        "min_level": int(parts[2]),
                        "max_level": int(parts[3])
                    }

        elif key == "conditions":
            if value and value.lower() != "none":
                map_data["conditions"] = value.split("|")
            else:
                map_data["conditions"] = []

    return map_data


def save_map(path, map_data):
    lines = []

    lines.append(f"inside:{str(map_data['inside']).lower()}")

    if map_data["objects"]:
        object_strings = []
        for obj in map_data["objects"]:
            object_strings.append(f"{obj['type']},{obj['x']},{obj['y']},{obj['data']}")
        lines.append("objects:" + "|".join(object_strings))
    else:
        lines.append("objects:none")

    if map_data["warps"]:
        warp_strings = []
        for warp in map_data["warps"]:
            warp_strings.append(
                f"{warp['x']},{warp['y']},{warp['target_map']},{warp['target_x']},{warp['target_y']}"
            )
        lines.append("warps:" + "|".join(warp_strings))
    else:
        lines.append("warps:none")

    if map_data["connections"]:
        connection_strings = []
        for connection in map_data["connections"]:
            connection_strings.append(
                f"{connection['direction']},{connection['destination']},{connection['offset']}"
            )
        lines.append("connections:" + "|".join(connection_strings))
    else:
        lines.append("connections:none")

    if map_data["wild"] is not None:
        wild = map_data["wild"]
        lines.append(
            f"wild:{wild['terrain']},{wild['rate']},{wild['min_level']},{wild['max_level']}"
        )
    else:
        lines.append("wild:none")

    if map_data["conditions"]:
        lines.append("conditions:" + "|".join(map_data["conditions"]))
    else:
        lines.append("conditions:none")

    lines.append("configuration:")

    for row in map_data["tiles"]:
        lines.append(",".join(row))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# =========================
# TILE LOADING
# =========================
def load_tile_surfaces(tile_folder):
    tile_surfaces = {}

    if not os.path.exists(tile_folder):
        print(f"Tile folder not found: {tile_folder}")
        return tile_surfaces

    for filename in sorted(os.listdir(tile_folder)):
        if not filename.lower().endswith(".png"):
            continue

        tile_id = filename[:-4]
        full_path = os.path.join(tile_folder, filename)

        try:
            image = pygame.image.load(full_path).convert_alpha()
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            tile_surfaces[tile_id] = image
        except Exception as e:
            print(f"Failed to load tile {filename}: {e}")

    return tile_surfaces


def make_palette_surfaces(tile_surfaces):
    palette_surfaces = {}
    for tile_id, surf in tile_surfaces.items():
        palette_surfaces[tile_id] = pygame.transform.scale(
            surf, (PALETTE_TILE_SIZE, PALETTE_TILE_SIZE)
        )
    return palette_surfaces


def make_missing_tile_surface(tile_id, size):
    surf = pygame.Surface((size, size))
    surf.fill((255, 0, 255))
    font = pygame.font.SysFont(None, 18)
    text = font.render(tile_id[-2:], True, (0, 0, 0))
    rect = text.get_rect(center=(size // 2, size // 2))
    surf.blit(text, rect)
    return surf


# =========================
# DRAWING
# =========================
def draw_map(screen, map_data, tile_surfaces, camera_x, camera_y, font):
    tiles = map_data["tiles"]

    for y, row in enumerate(tiles):
        for x, tile_id in enumerate(row):
            draw_x = x * TILE_SIZE - camera_x
            draw_y = y * TILE_SIZE - camera_y

            if tile_id in tile_surfaces:
                screen.blit(tile_surfaces[tile_id], (draw_x, draw_y))
            else:
                missing = make_missing_tile_surface(tile_id, TILE_SIZE)
                screen.blit(missing, (draw_x, draw_y))

            pygame.draw.rect(screen, (60, 60, 60), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)

    # Draw object markers
    for obj in map_data["objects"]:
        draw_x = obj["x"] * TILE_SIZE - camera_x
        draw_y = obj["y"] * TILE_SIZE - camera_y
        pygame.draw.rect(screen, (255, 200, 0), (draw_x + 8, draw_y + 8, 16, 16))
        label = font.render("O", True, (0, 0, 0))
        screen.blit(label, (draw_x + 11, draw_y + 8))

    # Draw warp markers
    for warp in map_data["warps"]:
        draw_x = warp["x"] * TILE_SIZE - camera_x
        draw_y = warp["y"] * TILE_SIZE - camera_y
        pygame.draw.rect(screen, (0, 200, 255), (draw_x + 8, draw_y + 8, 16, 16))
        label = font.render("W", True, (0, 0, 0))
        screen.blit(label, (draw_x + 10, draw_y + 8))


def draw_sidebar(
    screen,
    screen_width,
    screen_height,
    tile_ids,
    palette_surfaces,
    selected_tile,
    font,
    palette_scroll,
    selected_tool
):
    sidebar_rect = pygame.Rect(screen_width - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, screen_height)
    pygame.draw.rect(screen, (30, 30, 30), sidebar_rect)

    screen.set_clip(sidebar_rect)

    title = font.render("Palette", True, (255, 255, 255))
    screen.blit(title, (screen_width - SIDEBAR_WIDTH + 12, 12))

    info_y = 40
    selected_text = font.render(f"Selected: {selected_tile}", True, (255, 255, 255))
    screen.blit(selected_text, (screen_width - SIDEBAR_WIDTH + 12, info_y))

    tool_text = font.render(f"Tool: {selected_tool}", True, (255, 255, 255))
    screen.blit(tool_text, (screen_width - SIDEBAR_WIDTH + 12, info_y + 24))

    help_lines = [
        "LMB: use tool",
        "RMB: pick tile",
        "Scroll: palette",
        "Arrows: move map",
        "S: save",
        "O: open map",
        "N: new map"
    ]

    help_y = info_y + 52
    for line in help_lines:
        surf = font.render(line, True, (180, 180, 180))
        screen.blit(surf, (screen_width - SIDEBAR_WIDTH + 12, help_y))
        help_y += 20

    # Tool buttons
    tools_y = help_y + 8
    tools_x = screen_width - SIDEBAR_WIDTH + 12

    paint_rect = pygame.Rect(tools_x, tools_y, 56, 30)
    warp_rect = pygame.Rect(tools_x + 62, tools_y, 56, 30)
    eraser_rect = pygame.Rect(tools_x + 124, tools_y, 56, 30)

    paint_fill = (140, 140, 60) if selected_tool == "paint" else (70, 70, 70)
    warp_fill = (60, 120, 160) if selected_tool == "warp" else (70, 70, 70)
    eraser_fill = (140, 70, 70) if selected_tool == "eraser" else (70, 70, 70)

    pygame.draw.rect(screen, paint_fill, paint_rect)
    pygame.draw.rect(screen, warp_fill, warp_rect)
    pygame.draw.rect(screen, eraser_fill, eraser_rect)

    pygame.draw.rect(screen, (220, 220, 220), paint_rect, 2)
    pygame.draw.rect(screen, (220, 220, 220), warp_rect, 2)
    pygame.draw.rect(screen, (220, 220, 220), eraser_rect, 2)

    screen.blit(font.render("Paint", True, (255, 255, 255)), (paint_rect.x + 6, paint_rect.y + 7))
    screen.blit(font.render("Warp", True, (255, 255, 255)), (warp_rect.x + 10, warp_rect.y + 7))
    screen.blit(font.render("Erase", True, (255, 255, 255)), (eraser_rect.x + 5, eraser_rect.y + 7))

    palette_start_y = tools_y + 44
    palette_start_x = screen_width - SIDEBAR_WIDTH + PALETTE_PADDING

    palette_rects = {}
    tool_rects = {
        "paint": paint_rect,
        "warp": warp_rect,
        "eraser": eraser_rect
    }

    for i, tile_id in enumerate(tile_ids):
        col = i % PALETTE_COLUMNS
        row = i // PALETTE_COLUMNS

        x = palette_start_x + col * (PALETTE_TILE_SIZE + PALETTE_PADDING)
        y = palette_start_y + row * (PALETTE_TILE_SIZE + 24) - palette_scroll

        rect = pygame.Rect(x, y, PALETTE_TILE_SIZE, PALETTE_TILE_SIZE)
        palette_rects[tile_id] = rect

        if rect.bottom < 0 or rect.top > screen_height:
            continue

        if tile_id in palette_surfaces:
            screen.blit(palette_surfaces[tile_id], rect.topleft)
        else:
            missing = make_missing_tile_surface(tile_id, PALETTE_TILE_SIZE)
            screen.blit(missing, rect.topleft)

        border_color = (255, 255, 0) if tile_id == selected_tile else (100, 100, 100)
        pygame.draw.rect(screen, border_color, rect, 2)

        label = font.render(tile_id, True, (220, 220, 220))
        screen.blit(label, (x, y + PALETTE_TILE_SIZE + 2))

    screen.set_clip(None)
    return palette_rects, tool_rects, palette_start_y


# =========================
# HELPERS
# =========================
def get_map_dimensions(map_data):
    height = len(map_data["tiles"])
    width = len(map_data["tiles"][0]) if height > 0 else 0
    return width, height


def build_blank_map(width, height, fill_tile="0001"):
    return {
        "inside": False,
        "objects": [],
        "warps": [],
        "connections": [],
        "wild": None,
        "conditions": [],
        "tiles": [[fill_tile for _ in range(width)] for _ in range(height)]
    }


def resize_screen_for_map(map_data):
    map_width, map_height = get_map_dimensions(map_data)

    desired_width = WINDOW_WIDTH
    desired_height = WINDOW_HEIGHT

    screen_width = max(MIN_WINDOW_WIDTH, min(desired_width, MAX_WINDOW_WIDTH))
    screen_height = max(MIN_WINDOW_HEIGHT, min(desired_height, MAX_WINDOW_HEIGHT))

    screen = pygame.display.set_mode((screen_width, screen_height))
    return screen, screen_width, screen_height, map_width, map_height


def draw_text_input_overlay(screen, screen_width, screen_height, font, prompt, current_text):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    box_w = min(500, screen_width - 40)
    box_h = 120
    box_x = (screen_width - box_w) // 2
    box_y = (screen_height - box_h) // 2

    pygame.draw.rect(screen, (40, 40, 40), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, (220, 220, 220), (box_x, box_y, box_w, box_h), 2)

    prompt_surf = font.render(prompt, True, (255, 255, 255))
    screen.blit(prompt_surf, (box_x + 16, box_y + 16))

    text_surf = font.render(current_text + "|", True, (255, 255, 0))
    screen.blit(text_surf, (box_x + 16, box_y + 56))


def screen_to_tile(mx, my, camera_x, camera_y):
    tile_x = (mx + camera_x) // TILE_SIZE
    tile_y = (my + camera_y) // TILE_SIZE
    return int(tile_x), int(tile_y)


def paint_tile(map_data, x, y, tile_id):
    width, height = get_map_dimensions(map_data)
    if 0 <= x < width and 0 <= y < height:
        map_data["tiles"][y][x] = tile_id

def remove_warp_at(map_data, x, y):
    before = len(map_data["warps"])
    map_data["warps"] = [
        warp for warp in map_data["warps"]
        if not (warp["x"] == x and warp["y"] == y)
    ]
    return len(map_data["warps"]) < before


def remove_object_at(map_data, x, y):
    before = len(map_data["objects"])
    map_data["objects"] = [
        obj for obj in map_data["objects"]
        if not (obj["x"] == x and obj["y"] == y)
    ]
    return len(map_data["objects"]) < before


def erase_at(map_data, x, y):
    removed_warp = remove_warp_at(map_data, x, y)
    removed_object = remove_object_at(map_data, x, y)
    return removed_warp or removed_object

def draw_map_scrollbar(screen, screen_width, screen_height, map_width, map_height, camera_x, camera_y):
    view_width = screen_width - SIDEBAR_WIDTH
    view_height = screen_height

    content_width = map_width * TILE_SIZE
    content_height = map_height * TILE_SIZE

    if content_width > view_width:
        bar_width = view_width * (view_width / content_width)
        scroll_ratio_x = camera_x / (content_width - view_width)
        bar_x = scroll_ratio_x * (view_width - bar_width)

        pygame.draw.rect(screen, (50, 50, 50), (0, view_height - 10, view_width, 10))
        pygame.draw.rect(screen, (180, 180, 180), (bar_x, view_height - 10, bar_width, 10))

    if content_height > view_height:
        bar_height = view_height * (view_height / content_height)
        scroll_ratio_y = camera_y / (content_height - view_height)
        bar_y = scroll_ratio_y * (view_height - bar_height)

        pygame.draw.rect(screen, (50, 50, 50), (view_width - 10, 0, 10, view_height))
        pygame.draw.rect(screen, (180, 180, 180), (view_width - 10, bar_y, 10, bar_height))


def draw_palette_scrollbar(screen, screen_width, palette_height, visible_height, palette_scroll, palette_start_y):
    if palette_height <= visible_height or visible_height <= 0:
        return

    bar_height = visible_height * (visible_height / palette_height)
    scroll_ratio = palette_scroll / (palette_height - visible_height) if palette_height > visible_height else 0
    bar_y = palette_start_y + scroll_ratio * (visible_height - bar_height)

    pygame.draw.rect(screen, (50, 50, 50), (screen_width - 12, palette_start_y, 8, visible_height))
    pygame.draw.rect(screen, (180, 180, 180), (screen_width - 12, bar_y, 8, bar_height))


# =========================
# MAIN
# =========================
def main():
    pygame.init()
    pygame.display.set_caption("Pokemon Map Editor")
    font = pygame.font.SysFont(None, 22)
    clock = pygame.time.Clock()

    current_map_path = MAP_FILE
    current_map_id = os.path.splitext(os.path.basename(current_map_path))[0]
    map_data = load_map(current_map_path)
    palette_scroll = 0

    screen, screen_width, screen_height, map_width, map_height = resize_screen_for_map(map_data)

    tile_surfaces = load_tile_surfaces(TILE_FOLDER)
    palette_surfaces = make_palette_surfaces(tile_surfaces)
    tile_ids = sorted(tile_surfaces.keys())

    if not tile_ids:
        print("No tile images found. Put tile PNGs in the tiles folder.")
        pygame.quit()
        return

    selected_tile = tile_ids[0]
    selected_tool = "paint"

    camera_x = 0
    camera_y = 0

    running = True
    mouse_painting = False
    input_mode = None
    input_text = ""
    pending_new_width = None

    pending_warp_tile = None
    pending_warp = {
        "target_map": "",
        "target_x": None,
        "target_y": None
    }

    while running:
        clock.tick(FPS)

        # Palette layout info used both before and after drawing
        tiles_per_row = PALETTE_COLUMNS
        total_rows = (len(tile_ids) + tiles_per_row - 1) // tiles_per_row

        # This matches the sidebar layout:
        # title + info + help + tools + padding
        palette_start_y = 40 + 52 + (7 * 20) + 8 + 44
        palette_height = total_rows * (PALETTE_TILE_SIZE + 24)
        visible_height = screen_height - palette_start_y
        max_scroll = max(0, palette_height - visible_height)
        palette_scroll = max(0, min(palette_scroll, max_scroll))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if input_mode is not None:
                    if event.key == pygame.K_ESCAPE:
                        input_mode = None
                        input_text = ""
                        pending_new_width = None
                        pending_warp_tile = None
                        pending_warp = {
                            "target_map": "",
                            "target_x": None,
                            "target_y": None
                        }

                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]

                    elif event.key == pygame.K_RETURN:
                        if input_mode == "map_id":
                            new_map_id = input_text.strip()
                            if new_map_id:
                                new_map_path = os.path.join("resources", "maps", f"{new_map_id}.map")
                                if os.path.exists(new_map_path):
                                    current_map_id = new_map_id
                                    current_map_path = new_map_path
                                    map_data = load_map(current_map_path)
                                    screen, screen_width, screen_height, map_width, map_height = resize_screen_for_map(map_data)
                                    camera_x = 0
                                    camera_y = 0
                                    print(f"Loaded map: {current_map_path}")
                                else:
                                    print(f"Map does not exist: {new_map_path}")
                            input_mode = None
                            input_text = ""

                        elif input_mode == "new_map_id":
                            new_map_id = input_text.strip()
                            if new_map_id:
                                current_map_id = new_map_id
                                current_map_path = os.path.join("resources", "maps", f"{current_map_id}.map")
                                input_mode = "new_width"
                                input_text = ""
                            else:
                                print("Map id cannot be blank.")
                                input_text = ""

                        elif input_mode == "new_width":
                            try:
                                pending_new_width = int(input_text)
                                if pending_new_width <= 0:
                                    raise ValueError
                                input_mode = "new_height"
                                input_text = ""
                            except ValueError:
                                print("Width must be a positive integer.")
                                input_text = ""

                        elif input_mode == "new_height":
                            try:
                                new_height = int(input_text)
                                if new_height <= 0:
                                    raise ValueError

                                map_data = build_blank_map(pending_new_width, new_height, selected_tile)
                                screen, screen_width, screen_height, map_width, map_height = resize_screen_for_map(map_data)
                                camera_x = 0
                                camera_y = 0

                                print(f"Built new blank map '{current_map_id}' at {pending_new_width}x{new_height}")
                                print(f"Press S to save to: {current_map_path}")

                                input_mode = None
                                input_text = ""
                                pending_new_width = None

                            except ValueError:
                                print("Height must be a positive integer.")
                                input_text = ""

                        elif input_mode == "warp_target_map":
                            target_map = input_text.strip()
                            if target_map:
                                pending_warp["target_map"] = target_map
                                input_mode = "warp_target_x"
                                input_text = ""
                            else:
                                print("Destination map cannot be blank.")
                                input_text = ""

                        elif input_mode == "warp_target_x":
                            try:
                                pending_warp["target_x"] = int(input_text)
                                input_mode = "warp_target_y"
                                input_text = ""
                            except ValueError:
                                print("Target X must be an integer.")
                                input_text = ""

                        elif input_mode == "warp_target_y":
                            try:
                                pending_warp["target_y"] = int(input_text)

                                if pending_warp_tile is not None:
                                    warp_x, warp_y = pending_warp_tile

                                    remove_warp_at(map_data, warp_x, warp_y)

                                    map_data["warps"].append({
                                        "x": warp_x,
                                        "y": warp_y,
                                        "target_map": pending_warp["target_map"],
                                        "target_x": pending_warp["target_x"],
                                        "target_y": pending_warp["target_y"]
                                    })
                                    print(
                                        f"Placed warp at ({warp_x}, {warp_y}) -> "
                                        f"{pending_warp['target_map']} "
                                        f"({pending_warp['target_x']}, {pending_warp['target_y']})"
                                    )

                                pending_warp_tile = None
                                pending_warp = {
                                    "target_map": "",
                                    "target_x": None,
                                    "target_y": None
                                }
                                input_mode = None
                                input_text = ""

                            except ValueError:
                                print("Target Y must be an integer.")
                                input_text = ""

                    else:
                        if event.unicode.isprintable():
                            input_text += event.unicode

                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_s:
                        save_map(current_map_path, map_data)
                        print(f"Saved map to {current_map_path}")

                    elif event.key == pygame.K_o:
                        input_mode = "map_id"
                        input_text = ""

                    elif event.key == pygame.K_n:
                        input_mode = "new_map_id"
                        input_text = ""
                        pending_new_width = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if mx >= screen_width - SIDEBAR_WIDTH:
                    palette_rects, tool_rects, _ = draw_sidebar(
                        screen,
                        screen_width,
                        screen_height,
                        tile_ids,
                        palette_surfaces,
                        selected_tile,
                        font,
                        palette_scroll,
                        selected_tool
                    )

                    for tool_name, rect in tool_rects.items():
                        if rect.collidepoint(mx, my):
                            selected_tool = tool_name
                            break
                    else:
                        for tile_id, rect in palette_rects.items():
                            if rect.collidepoint(mx, my):
                                selected_tile = tile_id
                                break

                else:
                    tile_x, tile_y = screen_to_tile(mx, my, camera_x, camera_y)
                    width, height = get_map_dimensions(map_data)

                    if event.button == 1:
                        if 0 <= tile_x < width and 0 <= tile_y < height:
                            if selected_tool == "paint":
                                paint_tile(map_data, tile_x, tile_y, selected_tile)
                                mouse_painting = True

                            elif selected_tool == "warp":
                                pending_warp_tile = (tile_x, tile_y)
                                pending_warp = {
                                    "target_map": "",
                                    "target_x": None,
                                    "target_y": None
                                }
                                input_mode = "warp_target_map"
                                input_text = ""

                            elif selected_tool == "eraser":
                                erased = erase_at(map_data, tile_x, tile_y)
                                mouse_painting = True
                                if erased:
                                    print(f"Erased content at ({tile_x}, {tile_y})")

                    elif event.button == 3:
                        if 0 <= tile_x < width and 0 <= tile_y < height:
                            picked = map_data["tiles"][tile_y][tile_x]
                            if picked in tile_ids:
                                selected_tile = picked

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_painting = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_painting:
                    mx, my = event.pos
                    if mx < screen_width - SIDEBAR_WIDTH:
                        tile_x, tile_y = screen_to_tile(mx, my, camera_x, camera_y)

                        if selected_tool == "paint":
                            paint_tile(map_data, tile_x, tile_y, selected_tile)
                        elif selected_tool == "eraser":
                            erase_at(map_data, tile_x, tile_y)

            elif event.type == pygame.MOUSEWHEEL:
                palette_scroll -= event.y * 20

        keys = pygame.key.get_pressed()

        if input_mode is None:
            if keys[pygame.K_LEFT]:
                camera_x -= 8
            if keys[pygame.K_RIGHT]:
                camera_x += 8
            if keys[pygame.K_UP]:
                camera_y -= 8
            if keys[pygame.K_DOWN]:
                camera_y += 8

        max_camera_x = max(0, map_width * TILE_SIZE - (screen_width - SIDEBAR_WIDTH))
        max_camera_y = max(0, map_height * TILE_SIZE - screen_height)
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        screen.fill((0, 0, 0))

        draw_map(screen, map_data, tile_surfaces, camera_x, camera_y, font)
        draw_map_scrollbar(screen, screen_width, screen_height, map_width, map_height, camera_x, camera_y)

        _, _, actual_palette_start_y = draw_sidebar(
            screen,
            screen_width,
            screen_height,
            tile_ids,
            palette_surfaces,
            selected_tile,
            font,
            palette_scroll,
            selected_tool
        )

        visible_height = screen_height - actual_palette_start_y
        max_scroll = max(0, palette_height - visible_height)
        palette_scroll = max(0, min(palette_scroll, max_scroll))

        draw_palette_scrollbar(
            screen,
            screen_width,
            palette_height,
            visible_height,
            palette_scroll,
            actual_palette_start_y
        )

        if input_mode == "map_id":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter map_id to load:", input_text)
        elif input_mode == "new_map_id":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter new map_id:", input_text)
        elif input_mode == "new_width":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter new map width:", input_text)
        elif input_mode == "new_height":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter new map height:", input_text)
        elif input_mode == "warp_target_map":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter destination map:", input_text)
        elif input_mode == "warp_target_x":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter destination X:", input_text)
        elif input_mode == "warp_target_y":
            draw_text_input_overlay(screen, screen_width, screen_height, font, "Enter destination Y:", input_text)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()