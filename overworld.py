# -*- coding: utf-8 -*-
"""
This file handles everything to do with the overworld stages
"""
#python modules
import pygame
import math
import random
import pokemon
from dex import dex
 
#other data

#the final size of the tile in game will match character sprites
tilesize = 64

startingcoords = [2,2]
tiles = {}
warpcoords = [2,2]
warpmap = ['']
warptype = ['']
def getstagefromfile(stageid, coords=startingcoords):
    #load a stage from a stage file
    wild_ = []
    height_ = 0
    width_ = 0
    tiledata_ = []
    mapdataline = 0
    objects_ = []
    warps_ = []
    amtwarps = -1
    events_ = {}
    for line in open('resources/maps/' + stageid + '.map'):
        if 'height:' in line:
            height_ = int(line[7:].strip('\n'))
        elif 'width:' in line:
            width_ = int(line[6:].strip('\n'))
        elif 'wild:' in line:
            for mon in line[4:].strip('\n').split('|'):
                wild_.append(mon)
        elif 'objects:' in line:
            for object_ in line[7:].strip('\n').split(','):
                objects_.append(object_)
        elif 'warps:' in line:
            for trio in line[6:].strip('\n').split('/'):
                warps_.append(trio)
                amtwarps += 1
        elif 'events:' in line:
            for event in line[7:].strip('\n').split(','):
                if not event == '':
                    events_[int(event.split('.')[0])] = event.split('.')[1]
        elif 'configuration:' in line:
            pass
        else:
            tiledata_.append([])
            for tile in ''.join(c for c in line if c not in '\n ').split(','):
                tiledata_[mapdataline].append(int(tile))
            mapdataline += 1
    
    for i in range(2):
        wild_[i] = wild_[i].split(',')
        wild_[i][1] = wild_[i][1].split('.')
        
    
    for i in range(amtwarps + 1):
        warps_[i] = warps_[i].split('|')
        for j in range(2):
            warps_[i][j] = warps_[i][j].split(',')
            for k in range(2):
                if j != 2:
                    warps_[i][j][k] = int(warps_[i][j][k])
    instage = Stage(width_, height_, objects_, warps_, events_, coords, wild_)
    instage.tiledata = tiledata_
    return instage

def settiles():
    # Load 32x32 tiles and scale to 64x64
    tiles[1] = pygame.transform.scale(
        pygame.image.load("graphics/tiles/0001.png").convert(), (tilesize, tilesize)
        )
    tiles[2] = pygame.transform.scale(
        pygame.image.load("graphics/tiles/0002.png").convert(), (tilesize, tilesize)
        )
    tiles[3] = pygame.transform.scale(
        pygame.image.load("graphics/tiles/0003.png").convert(), (tilesize, tilesize))

def checkwarp(gamemap):
    for warp in gamemap.warps:
        if warp[0][0] == gamemap.position[0] and warp[0][1] == gamemap.position[1]:
            warpcoords[0] = warp[1][0]
            warpcoords[1] = warp[1][1]
            warpmap[0] = warp[2]
            warptype[0] = warp[3]
            return True
    return False

def warpplayer():
    return getstagefromfile(warpmap[0], warpcoords)

def checkwildbattle(gamemap):
    if gamemap.get_tile(gamemap.position[1], gamemap.position[0]) in [3]:
        #apparently it is an 11% chance
        if gamemap.wild[0][2].isnumeric():
            if random.randint(0, 99) < 11:
                return True
    elif gamemap.get_tile(gamemap.position[1], gamemap.position[0]) in [4]:
        #apparently it is an 11% chance
        if gamemap.wild[1][2].isnumeric():
            if random.randint(0, 99) < 11:
                return True
    return False

def getwildpokemon(gamemap):
    if gamemap.get_tile(gamemap.position[1], gamemap.position[0]) in [3]:
        pokemonhere = dex[int(random.choice(gamemap.wild[0][2:]))]
        return pokemon.Pokemon(random.randint(int(gamemap.wild[0][1][0]), int(gamemap.wild[0][1][1])), pokemonhere)
    elif gamemap.get_tile(gamemap.position[1], gamemap.position[0]) in [4]:
        pokemonhere = dex[int(random.choice(gamemap.wild[1][2:]))]
        return pokemon.Pokemon(random.randint(int(gamemap.wild[1][1][0]), int(gamemap.wild[1][1][1])), pokemonhere)


class Stage:
    def __init__(self, width, height, objects, warps, events, position, wild):
        self.width = width
        self.height = height
        self.objects = objects
        self.warps = warps
        self.events = events
        self.position = position
        self.wild = wild
        self.tiledata = [[0 for _ in range(width)] for _ in range(height)]

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiledata[y][x]
        return 0  # Treat out-of-bounds as impassable

    def is_passable(self, x, y):
        return self.get_tile(x, y) == 1 or self.get_tile(x, y) == 3
    
    def draw(self, surface, offset_x, offset_y):
        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.tiledata[y][x]
                tile_image = tiles[tile_id]
                draw_x = x * tilesize + offset_x
                draw_y = y * tilesize + offset_y
                surface.blit(tile_image, (draw_x, draw_y))