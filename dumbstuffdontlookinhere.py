# -*- coding: utf-8 -*-
"""
uhh...
"""

import pygame

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

#if a map calls for mario 1-1, have it route here and make it LITERALLY mario 1-1; Direction is allowed as you can go back; if you die, you go back to wherever you started:
class DOTHEMARIO:
    def __init__(self, screen, direction='right'):
        self.screen = screen
        self.direction = direction
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 100, 255)
        self.GROUND_HEIGHT = 640 - 50
        
        # Player settings
        self.PLAYER_WIDTH = 50
        self.PLAYER_HEIGHT = 50
        self.JUMP_STRENGTH = -15
        self.GRAVITY = 0.8
        
        # Player data
        self.player_x = 832 // 2
        self.player_y = self.GROUND_HEIGHT - self.PLAYER_HEIGHT
        self.player_y_velocity = 0
        self.is_jumping = False
    
    def SWINGYOURARMS(self):
        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z] and not self.is_jumping:
            self.player_y_velocity = self.JUMP_STRENGTH
            self.is_jumping = True
    
        # Apply gravity
        self.player_y_velocity += self.GRAVITY
        self.player_y += self.player_y_velocity
    
        # Ground collision
        if self.player_y + self.PLAYER_HEIGHT >= self.GROUND_HEIGHT:
            self.player_y = self.GROUND_HEIGHT - self.PLAYER_HEIGHT
            self.player_y_velocity = 0
            self.is_jumping = False
    
        # Drawing
        self.screen.fill(self.WHITE)
        pygame.draw.rect(self.screen, self.BLUE, (self.player_x, self.player_y, self.PLAYER_WIDTH, self.PLAYER_HEIGHT))
        pygame.draw.rect(self.screen, (0, 200, 0), (0, self.GROUND_HEIGHT, 832, 640 - self.GROUND_HEIGHT))  # ground
        
        return True
        
