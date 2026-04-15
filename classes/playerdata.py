# -*- coding: utf-8 -*-
"""
Handles the player's save data and in game saved stuff about the player
"""
import pygame

from classes import pokemon

class Player:
    def __init__(self, name, sprite, party, bag):
        self.name = name
        self.sprite = sprite
        self.party = party
        self.bag = bag

    def add_item(self, item):
        pass

def build_overworld_skin(player, tilesize=50):

    player_sprites = {}
    player_sprites['e_1'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_east_1.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['e_2'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_east_2.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['e_3'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_east_3.png").convert_alpha(), (tilesize, tilesize))

    player_sprites['n_1'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_north_1.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['n_2'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_north_2.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['n_3'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_north_3.png").convert_alpha(), (tilesize, tilesize))

    player_sprites['s_1'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_south_1.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['s_2'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_south_2.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['s_3'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_south_3.png").convert_alpha(), (tilesize, tilesize))

    player_sprites['w_1'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_west_1.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['w_2'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_west_2.png").convert_alpha(), (tilesize, tilesize))
    player_sprites['w_3'] = pygame.transform.scale(pygame.image.load(f"graphics/sprites/player/{player.sprite}_west_3.png").convert_alpha(), (tilesize, tilesize))

    return player_sprites

def set_skin(player, sprite):
    player.sprite = sprite

def choose_name(player, name):
    player.name = name

def choose_starter(player, starter):
    mon_id = 1 if starter == 'peblet' else 4 if starter == 'guardil' else 7
    player.party.append(pokemon.Pokemon(5, mon_id))

def get_player_party(player):
    # Placeholder for loading player party from save data
    return player.party

def displaypokedex():
    pass

def displayplayer():
    pass

def displayparty():
    pass

def displaybag():
    pass
