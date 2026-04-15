# -*- coding: utf-8 -*-
"""
Handles In game Pokemon
"""

import pygame
import math
import random

from classes.dex import get_dex as dex
from classes import abilities
from classes import moves

natures = {
    1:'Docile',
    2:'Adamant',
    3:'Brave',
    4:'Lonely',
    5:'Naughty',
    6:'Bold',
    7:'Impish',
    8:'Lax',
    9:'Relaxed',
    10:'Modest',
    11:'Mild',
    12:'Quiet',
    13:'Rash',
    14:'Calm',
    15:'Careful',
    16:'Gentle',
    17:'Sassy',
    18:'Hasty',
    19:'Jolly',
    20:'Naive',
    21:'Timid'
    }

#creates a pokemon 
class Pokemon:
    def __init__(self, level, dexno, status='none', item='unspecified', currenthp='max', nature=0, ability=0, nickname='', evs = None, ivs = None, movechanges = None, experience=0, statchanges=None):
        self.level = level
        self.dexno = dexno
        self.currenthp = currenthp
        self.ability = ability
        self.evs = evs.copy() if evs is not None else {'hp':0,'atk':0,'def':0,'spa':0,'spd':0,'spe':0}
        self.ivs = ivs.copy() if ivs is not None else {'hp':0,'atk':0,'def':0,'spa':0,'spd':0,'spe':0}
        self.movechanges = movechanges.copy() if movechanges is not None else {1:0,2:0,3:0,4:0}
        self.nickname = nickname
        self.shiny = False
        self.moves = {}
        self.nature = nature
        self.status = status
        self.item = item
        self.fainted = False
        self.sprite = dex()[dexno]['sprite']
        self.experience = experience
        self.statchanges = statchanges.copy() if statchanges is not None else {'atk':0,'def':0,'spa':0,'spd':0,'spe':0}
        
        
        #randomly grab one of possible abilities if not given
        if self.ability == 0:
            self.ability = random.choice(dex()[self.dexno]['ability'])
        else:
            self.ability = ability
        
        #randomly set a nature if none is given
        if self.nature == 0:
            self.nature = natures[random.randint(1, 21)]
        
        #procedurally build movepool based on level
        counter = 0
        for j in dex()[self.dexno]['movepool']:
            if int(j) <= self.level:
                if isinstance(dex()[self.dexno]['movepool'][j], list):
                    for k in dex()[self.dexno]['movepool'][j]:
                        self.moves[counter + 1] = k
                        counter = (counter + 1) & 4
                else:
                    self.moves[counter + 1] = dex()[self.dexno]['movepool'][j]
                    counter = (counter + 1) % 4
                
        for i in self.movechanges:
            if not self.movechanges[i] == 0:
                self.moves[i] = self.movechanges[i]
                
        if self.item == 'unspecified':
            if len(dex()[self.dexno]['itempool']) >= 1:
                self.item = random.choice(dex()[self.dexno]['itempool'])
            else:
                self.item = 'none'
        for j in range(len(self.moves)):
            self.moves[j+1] = moves.buildmove(self.moves[j+1])
        
    #get the name and default to species name if unnamed
    def getname(self):
        if self.nickname == '':
            return dex()[self.dexno]['name']
        else:
            return self.nickname
        
    def checkfainted(self):
        if self.currenthp <= 0:
            self.fainted = True
        else:
            self.fainted = False

    def addexperience(self, amount):
        self.experience += amount
        if self.experience >= self.level ** 3:
            self.experience %= self.level ** 3
            self.level += 1
        
    #set the name
    def setname(self, name):
        self.nickname = name
    
    #change a move {moveslotnumber:move}
    def changemove(self, movechange):
        for i in movechange:
            if len(self.moves) < 4:
                self.moves[len(self.moves) + 1] = movechange[i]
                self.movechanges[len(self.moves) + 1] = movechange[i]
            else:
                self.movechanges[i] = movechange[i]
                self.moves[i] = movechange[i]
    
    #add ev values
    def addevs(self, ev, amount):
        if sum(self.evs.items()) + amount < 508:
            if self.evs[ev] + amount < 252:
                self.evs[ev] += amount
            else:
                self.evs[ev] = 252
        else:
            if self.evs[ev] + 508 - sum(self.evs.items()) < 252:
                self.evs[ev] += 508 - sum(self.evs.items())
            else:
                self.evs[ev] = 252
    
    #reset ev's to zero
    def resetevs(self):
        for i in self.evs:
            self.evs[i] = 0
    
    #generate iv values
    def genivs(self):
        for i in self.ivs:
            self.ivs[i] = random.randint(0, 31)
            
    #make it shiny
    def setshiny(self):
        self.shiny = True
    
    #roll for shiny
    def rollshiny(self, modifier):
        self.shiny = True if random.randint(1, 4096/modifier) == 420 else False
    
    def getbasestattotal(self):
        return dex()[self.dexno]['hp'] + dex()[self.dexno]['atk'] + dex()[self.dexno]['def'] + dex()[self.dexno]['spa'] + dex()[self.dexno]['spd'] + dex()[self.dexno]['spe']

    #get stats using actual formulas
    def getcurrenthp(self):
        if self.currenthp == 'max':
            return int(0.01 * (2 * dex()[self.dexno]['hp'] + self.ivs['hp'] + int(0.25 * self.evs['hp'])) * self.level) + self.level + 10
        else:
            return int(self.currenthp)
        
    def getmaxhp(self):
        return int(0.01 * (2 * dex()[self.dexno]['hp'] + self.ivs['hp'] + int(0.25 * self.evs['hp'])) * self.level) + self.level + 10
    
    def getatk(self, mod=1):
        naturemod = 1
        if self.nature == 'Adamant' or self.nature == 'Brave' or self.nature == 'Lonely' or self.nature == 'Naughty':
            naturemod = 1.1
        elif self.nature == 'Bold' or self.nature == 'Modest' or self.nature == 'Calm' or self.nature == 'Timid':
            naturemod = 0.9
        return int((((0.01 * (2 * dex()[self.dexno]['atk'] + self.ivs['atk'] + int(0.25 * self.evs['atk'])) * self.level) + 5) * naturemod) * mod)
    
    def getdef(self, mod=1):
        naturemod = 1
        if self.nature == 'Bold' or self.nature == 'Impish' or self.nature == 'Lax' or self.nature == 'Relaxed':
            naturemod = 1.1
        elif self.nature == 'Lonely' or self.nature == 'Mild' or self.nature == 'Gentle' or self.nature == 'Hasty':
            naturemod = 0.9
        return int((((0.01 * (2 * dex()[self.dexno]['def'] + self.ivs['def'] + int(0.25 * self.evs['def'])) * self.level) + 5) * naturemod) * mod)
    
    def getspa(self, mod=1):
        naturemod = 1
        if self.nature == 'Modest' or self.nature == 'Mild' or self.nature == 'Quiet' or self.nature == 'Rash':
            naturemod = 1.1
        elif self.nature == 'Adamant' or self.nature == 'Impish' or self.nature == 'Careful' or self.nature == 'Jolly':
            naturemod = 0.9
        return int((((0.01 * (2 * dex()[self.dexno]['spa'] + self.ivs['spa'] + int(0.25 * self.evs['spa'])) * self.level) + 5) * naturemod) * mod)
    
    def getspd(self, mod=1):
        naturemod = 1
        if self.nature == 'Calm' or self.nature == 'Careful' or self.nature == 'Gentle' or self.nature == 'Sassy':
            naturemod = 1.1
        elif self.nature == 'Naughty' or self.nature == 'Lax' or self.nature == 'Rash' or self.nature == 'Naive':
            naturemod = 0.9
        return int((((0.01 * (2 * dex()[self.dexno]['spd'] + self.ivs['spd'] + int(0.25 * self.evs['spd'])) * self.level) + 5) * naturemod) * mod)
    
    def getspe(self, mod=1):
        naturemod = 1
        if self.nature == 'Hasty' or self.nature == 'Jolly' or self.nature == 'Naive' or self.nature == 'Timid':
            naturemod = 1.1
        elif self.nature == 'Brave' or self.nature == 'Relaxed' or self.nature == 'Quiet' or self.nature == 'Sassy':
            naturemod = 0.9
        return int((((0.01 * (2 * dex()[self.dexno]['spe'] + self.ivs['spe'] + int(0.25 * self.evs['spe'])) * self.level) + 5) * naturemod) * mod)
    
    #heal and deal already calculated damage
    def changehp(self, damage):
        self.currenthp = self.getcurrenthp() - damage
        if self.currenthp <= 0:
            self.currenthp = 0
            self.fainted = True
    
    def raisestat(self, stat, stages):
        self.statchanges[stat] += stages
        if self.statchanges[stat] > 6:
            self.statchanges[stat] = 6
        elif self.statchanges[stat] < -6:
            self.statchanges[stat] = -6
    
    def changehppercentmax(self, damage):
        self.currenthp = int(self.getmaxhp() - self.getmaxhp() * damage)
        
    def changhppercentcurrent(self, damage):
        self.currenthp = int(self.getcurrenthp() - self.getcurrenthp() * damage)
        
    def getability(self):
        return abilities.buildability(self.ability)
    