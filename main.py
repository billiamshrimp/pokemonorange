"""
The main execution file containing game loops
"""

# Python modules
import pygame
import sys
import math

# Game modules
import overworld
from dex import dex
import battlescript
import pokemon
import moves
import playerdata
import dumbstuffdontlookinhere as uhh

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 832, 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokemon Orange")

clock = pygame.time.Clock()
FPS = 60

"""
Overworld Constants
"""
BLACK = (0, 0, 0)
TILE_SIZE = 64
MOVE_DURATION_BASE = 0.25
SPEED_MULTIPLIER_FAST = 2

overworld.settiles()

#gamefont
gamefont = pygame.font.Font("resources/font/munro.ttf", 52)
gamefontsmall = pygame.font.Font("resources/font/munro.ttf", 30)

# Load 64x64 player sprites (no scaling needed)
player_sprites = {}
player_sprites['d1'] = pygame.image.load("graphics/sprites/player/playerd1.png").convert_alpha()
player_sprites['d2'] = pygame.image.load("graphics/sprites/player/playerd2.png").convert_alpha()
player_sprites['d3'] = pygame.image.load("graphics/sprites/player/playerd3.png").convert_alpha()

player_sprites['u1'] = pygame.image.load("graphics/sprites/player/playeru1.png").convert_alpha()
player_sprites['u2'] = pygame.image.load("graphics/sprites/player/playeru2.png").convert_alpha()
player_sprites['u3'] = pygame.image.load("graphics/sprites/player/playeru3.png").convert_alpha()

player_sprites['l1'] = pygame.image.load("graphics/sprites/player/playerl1.png").convert_alpha()
player_sprites['l2'] = pygame.image.load("graphics/sprites/player/playerl2.png").convert_alpha()
player_sprites['l3'] = pygame.image.load("graphics/sprites/player/playerl3.png").convert_alpha()

player_sprites['r1'] = pygame.image.load("graphics/sprites/player/playerr1.png").convert_alpha()
player_sprites['r2'] = pygame.image.load("graphics/sprites/player/playerr2.png").convert_alpha()
player_sprites['r3'] = pygame.image.load("graphics/sprites/player/playerr3.png").convert_alpha()

player_rect = player_sprites['d1'].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

#menu stuff
overworldselecter = pygame.transform.scale(pygame.image.load("graphics/ui/overworldselecter.png").convert(), (32, 32))
overworldselectpositiondefault = [565, 45]
overworldselectposition = [565, 45]
overworldoptions = pygame.transform.scale(pygame.image.load("graphics/ui/overworldoptions.png").convert(), (280, 472))
overworldoptionsposition = [545, 5]
overworldoptiondescription = pygame.transform.scale(pygame.image.load("graphics/ui/overworldoptiondescription.png").convert(), (968, 156))
overworldoptiondescriptionposition = [-20, 500]
overworldmenuoptions = {0: 0,1: 60,2: 120,3: 180,4: 240,5: 300,6: 360}
overworldmenuoption = 0

#default map
game_map = overworld.getstagefromfile('playerhouse2')

enemyparty = {}
# Player logical grid position
player_grid = [0, 0]
player_grid[0] = game_map.position[1]
player_grid[1] = game_map.position[0]

# Scroll offset (camera position)
offset = [0, 0]
offset[0] = SCREEN_WIDTH // 2 - player_grid[0] * TILE_SIZE - TILE_SIZE // 2
offset[1] = SCREEN_HEIGHT // 2 - player_grid[1] * TILE_SIZE - TILE_SIZE // 2

# Movement state
moving = False
move_dir = (0, 0)
move_progress = 0
move_frames = 0
speed_per_frame = 0
facing = 'd'
movement = '1'
interacting = False

#gamestate: straight forward (title, overworld, battle, cutscene)
gamestate = 'overworld'
battletype = 'wild'
battlestage = 'default'
weather = 'none'
terrain = 'none'
menulayer = 'overworldmenu'

#dont look here
mario = uhh.DOTHEMARIO(screen)

keystates = {}
def waskeypressed(key_):
    keys_ = pygame.key.get_pressed()
    
    if keys_[key_]:
        if not keystates.get(key_, False):
            keystates[key_] = True
            return True
        
    else:
        keystates[key_] = False
    return False

# === MAIN GAME LOOP ===
while True:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    
    #main overworld loop
    if gamestate == 'overworld':
    
        #uhh
        if 'mario' in game_map.events.values():
            gamestate = 'oneone'
            continue
        
        # Start movement
        if not moving and not interacting:
            movement = '1'
            dir_x, dir_y = 0, 0
                
            if waskeypressed(pygame.K_RETURN):
                menulayer = 'overworldmenu'
                gamestate = 'pausemenu'
            
            if keys[pygame.K_LEFT]:
                dir_x = -1
                facing = 'l'
                movement = '1'
            elif keys[pygame.K_RIGHT]:
                dir_x = 1
                facing = 'r'
                movement = '1'
            elif keys[pygame.K_UP]:
                dir_y = -1
                facing = 'u'
                movement = '1'
            elif keys[pygame.K_DOWN]:
                dir_y = 1
                facing = 'd'
                movement = '1'
    
            target_x = player_grid[0] + dir_x
            target_y = player_grid[1] + dir_y
    
            if (dir_x != 0 or dir_y != 0) and game_map.is_passable(target_x, target_y):
                is_fast = keys[pygame.K_x]
                duration = MOVE_DURATION_BASE / SPEED_MULTIPLIER_FAST if is_fast else MOVE_DURATION_BASE
                move_frames = int(duration * FPS)
                speed_per_frame = TILE_SIZE / move_frames
    
                move_dir = (dir_x, dir_y)
                moving = True
                game_map.position[0] += dir_y
                game_map.position[1] += dir_x
                move_progress = 0
    
        # Smooth scrolling movement
        if moving:
            dx = -move_dir[0] * speed_per_frame
            dy = -move_dir[1] * speed_per_frame
            offset[0] += dx
            offset[1] += dy
            move_progress += 1
            if move_progress >= 0.75 * move_frames:
                movement = '3'
            elif move_progress >= 0.50 * move_frames:
                movement = '1'
            elif move_progress >= 0.25 * move_frames:
                movement = '2'
            else:
                movement = '1'
            if move_progress >= move_frames:
                moving = False
                player_grid[0] += move_dir[0]
                player_grid[1] += move_dir[1]
                
                
                # check if we need to warp the player and do so
                if overworld.checkwarp(game_map):
                    game_map = overworld.warpplayer()
                    player_grid[0] = game_map.position[1]
                    player_grid[1] = game_map.position[0]
                    offset[0] = SCREEN_WIDTH // 2 - player_grid[0] * TILE_SIZE - TILE_SIZE // 2
                    offset[1] = SCREEN_HEIGHT // 2 - player_grid[1] * TILE_SIZE - TILE_SIZE // 2
    
                #check if the player should enter battle
                if overworld.checkwildbattle(game_map):
                    enemyparty.clear()
                    enemyparty[1] = overworld.getwildpokemon(game_map)
                    battletype = 'wild'
                    battlestage = 'default'
                    gamestate = 'battle'
    
        # Draw map
        game_map.draw(screen, offset[0], offset[1])
        #print(offset_x, offset_y)
    
        # Draw player (fixed position)
        screen.blit(player_sprites[facing + movement], player_rect)
        
    #main battle loop
    elif gamestate == 'battle':
        
        if battlescript.turnstate[0] == 'battlestart':
            battlescript.enterBattle('default', battletype, playerdata.playerparty, enemyparty, weather, terrain)
            battlescript.draw(screen)
        
        elif battlescript.turnstate[0] == 'moveselect':
            battlescript.draw(screen)
            gamestate = battlescript.playerallowselection(battletype, gamefont, gamefontsmall, screen)
    
    #main menu loop
    elif gamestate == 'pausemenu':
        if menulayer == 'overworldmenu':
            #draw the map and player in the background first
            game_map.draw(screen, offset[0], offset[1])
            screen.blit(player_sprites[facing + movement], player_rect)

            #so we're actually gunna draw the menu before the input to make sliding into different menus smooth
            screen.blit(overworldoptiondescription, overworldoptiondescriptionposition)
            screen.blit(overworldoptions, overworldoptionsposition)
            screen.blit(overworldselecter, overworldselectposition)

            #look for player input
            if waskeypressed(pygame.K_UP):
                overworldmenuoption = (overworldmenuoption - 1) % 7
                overworldselectposition[1] = overworldselectpositiondefault[1] + overworldmenuoptions[overworldmenuoption]
            elif waskeypressed(pygame.K_DOWN):
                overworldmenuoption = (overworldmenuoption + 1) % 7
                overworldselectposition[1] = overworldselectpositiondefault[1] + overworldmenuoptions[overworldmenuoption]
            elif waskeypressed(pygame.K_RETURN) or waskeypressed(pygame.K_x):
                overworldselectposition = [565, 45]
                overworldmenuoption = 0
                gamestate = 'overworld'
            elif waskeypressed(pygame.K_z):
                if overworldmenuoption == 0:
                    menulayer = 'pokedex'
                elif overworldmenuoption == 1:
                    menulayer = 'playerparty'
                elif overworldmenuoption == 2:
                    menulayer = 'playerbag'
                elif overworldmenuoption == 3:
                    menulayer = 'playeroption'
                elif overworldmenuoption == 4:
                    menulayer = 'save'
                elif overworldmenuoption == 5:
                    menulayer = 'option'
                elif overworldmenuoption == 6:
                    overworldselectposition = [565, 45]
                    overworldmenuoption = 0
                    gamestate = 'overworld'
        elif menulayer == 'pokedex':
            if not playerdata.displaypokedex():
                menulayer = 'overworldmenu'
        elif menulayer == 'playerparty':
            if not playerdata.displayparty():
                menulayer = 'overworldmenu'
        elif menulayer == 'playerbag':
            if not playerdata.displaybag():
                menulayer = 'overworldmenu'
        elif menulayer == 'playermenu':
            if not playerdata.displayplayer():
                menulayer = 'overworldmenu'
        elif menulayer == 'save':
            pass
        elif menulayer == 'option':
            pass
    
    elif gamestate == 'oneone':
        if not mario.SWINGYOURARMS():
            gamestate = 'overworld'
        
    pygame.display.flip()
    clock.tick(FPS)