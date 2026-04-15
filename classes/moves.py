# -*- coding: utf-8 -*-
"""
Move Data and execution
"""
import random

from classes import pokemon
from classes.dex import get_dex as dex
from classes import typechart


moves = {
    'Tackle': [40, 35, 0, 1.0, 'Normal', 'Physical', {'contact': True}, 'Tackle'],
    'Howl': [0, 40, 0, 'cannotmiss', 'Normal', 'Status', {'selfraisestat' : ['atk', 1]}, 'Howl'],
    'Rock Throw': [50, 15, 0, 0.9, 'Rock', 'Physical', {}, 'Rock Throw'],
    'Rock Polish': [0, 20, 0, 'cannotmiss', 'Rock', 'Status', {'selfraisestat': ['spe', 2]}, 'Rock Polish'],
    'Rock Tomb': [60, 15, 0, 0.95, 'Rock', 'Physical', {'enemyraisestat': ['spe', -1]}, 'Rock Tomb'],
    'Rock Slide': [75, 10, 0, 0.9, 'Rock', 'Physical', {'contact': True, 'mayflinch': 0.3}, 'Rock Slide'],
    'Take Down': [90, 20, 0, 0.85, 'Normal', 'Physical', {'recoil': 0.25}, 'Take Down'],
    'Boulder Toss': [80, 15, 0, 1.0, 'Rock', 'Physical', {}, 'Boulder Toss'],
    'Sandstorm': [0, 10, 0, 'cannotmiss', 'Rock', 'Status', {'weather': 'Sandstorm'}, 'Sandstorm'],
    'Accelerock': [40, 20, 1, 1.0, 'Rock', 'Physical', {}, 'Accelerock'],
    'Double Edge': [120, 15, 0, 0.85, 'Normal', 'Physical', {'recoil': 0.25}, 'Double Edge'],
    'Cliff Dive': [300, 5, 0, 1.0, 'Rock', 'Physical', {'contact': True, 'selfko': True}, 'Cliff Dive'],
    'Seed Bomb': [80, 15, 0, 1.0, 'Grass', 'Physical', {}, 'Seed Bomb'],
    'Stealth Rock': [0, 20, 0, 'cannotmiss', 'Rock', 'Status', {'hazard': 'Stealth Rock'}, 'Stealth Rock'],
    'Rock Smash': [40, 15, 0, 0.9, 'Rock', 'Physical', {'contact': True, 'HM': True}, 'Rock Smash'],
    'Rock Climb': [90, 20, 0, 0.85, 'Rock', 'Physical', {'contact': True, 'HM': True}, 'Rock Climb'],
    'Grassy Glide': [55, 20, 0, 1.0, 'Grass', 'Physical', {'terrainboostpriority': 'Grassy Terrain'}, 'Grassy Glide'],
    'Pound': [40, 35, 0, 1.0, 'Normal', 'Physical', {'contact': True}, 'Pound'],
    'Metal Sound': [0, 40, 0, 0.85, 'Steel', 'Status', {'enemyraisestat': ['def', -2]}, 'Metal Sound'],
    'Smart Strike': [70, 15, 0, 'cannotmiss', 'Steel', 'Physical', {'contact': True}, 'Smart Strike'],
    'Iron Defense': [0, 15, 0, 'cannotmiss', 'Steel', 'Status', {'selfraisestat': ['def', 2]}, 'Iron Defense'],
    'Iron Head': [80, 15, 0, 0.9, 'Steel', 'Physical', {'contact': True, 'mayflinch': 0.3}, 'Iron Head'],
    'Recover': [0, 20, 0, 'cannotmiss', 'Normal', 'Status', {'heal': 0.5}, 'Recover'],
    'Shadow Sneak': [40, 30, 1, 1.0, 'Ghost', 'Physical', {'contact': True}, 'Shadow Sneak'],
    'Kings Shield': [0, 15, 4, 'cannotmiss', 'Steel', 'Status', {'protect': {'enemyraisestat': ['atk', -2]}}, 'Kings Shield'],
    'Taunt': [0, 15, 0, 'cannotmiss', 'Dark', 'Status', {'taunt': True}, 'Taunt'],
    'Body Press': [80, 15, 0, 1.0, 'Fighting', 'Physical', {'contact': True, 'defasatk': True}, 'Body Press'],
    'Spikes': [0, 25, 0, 'cannotmiss', 'Ground', 'Status', {'hazard': 'Spikes'}, 'Spikes'],
    'Toxic': [0, 15, 0, 0.9, 'Poison', 'Status', {'statusenemy': 'Toxic'}, 'Toxic'],
    'Block': [0, 5, 0, 'cannotmiss', 'Normal', 'Status', {'preventenemyescape': True}, 'Block'],
    'Protect': [0, 10, 4, 'cannotmiss', 'Normal', 'Status', {'protect': True}, 'Protect'],
    'Strength': [80, 15, 0, 1.0, 'Normal', 'Physical', {'HM': True}, 'Strength'],
    'Poison Powder': [0, 25, 0, 0.85, 'Poison', 'Status', {'statusenemy': 'Poison'}, 'Poison Powder'],
    'Ember': [30, 15, 0, 1.0, 'Fire', 'Special', {'chancestatusenemy': ['Burn', 0.1]}, 'Ember'],
    'Poison Sting': [30, 25, 0, 1.0, 'Poison', 'Physical', {'chancestatusenemy': ['Poison', 0.1]}, 'Poison Sting'],
    'Bubble': [30, 25, 0, 1.0, 'Water', 'Special', {'chanceenemyraisestat': ['spe', -1, 0.1]}, 'Bubble'],
    'Fire Spin': [15, 25, 0, 0.85, 'Fire', 'Special', {'partialtrap': 0.1}, 'Fire Spin'],
    'Rapid Spin': [50, 30, 0, 1.0, 'Normal', 'Physical', {'selfraisestat': ['spe', 1], 'freebindings': True}, 'Rapid Spin'],
    'Acid Armor': [0, 15, 0, 'cannotmiss', 'Poison', 'Status', {'selfraisestat': ['def', 2]}, 'Acid Armor'],
    'Sludge Wave': [95, 10, 0, 0.95, 'Poison', 'Special', {'chancestatusenemy': ['Poison', 0.1]}, 'Sludge Wave'],
    'Flamethrower': [90, 15, 0, 1.0, 'Fire', 'Special', {'chancestatusenemy': ['Burn', 0.1]}, 'Flamethrower'],
    'Overheat': [130, 10, 0, 0.9, 'Fire', 'Special', {'selfraisestat': ['spa', -2]}, 'Overheat'],
    'Nasty Plot': [0, 15, 0, 'cannotmiss', 'Dark', 'Status', {'selfraisestat': ['spa', 2]}, 'Nasty Plot'],
    'Sunny Day': [0, 5, 0, 'cannotmiss', 'Fire', 'Status', {'weather': 'Sun'}, 'Sunny Day'],
    'Hydro Pump': [110, 5, 0, 0.85, 'Water', 'Special', {}, 'Hydro Pump'],
    'Surf': [90, 15, 0, 1.0, 'Water', 'Special', {'HM': True}, 'Surf'],

    }
# Establishes a Move with effects being a dictionary of string keywords
def buildmove(name):
    return Move(moves[name][0], moves[name][1], moves[name][2], moves[name][3], moves[name][4], moves[name][5], moves[name][6], moves[name][7],)

class Move:
    def __init__(self, damage, pp, priority, accuracy, movetype, movecategory, effects, name, currentpp='max'):
        self.damage = damage
        self.pp = pp
        self.priority = priority
        self.accuracy = accuracy
        self.movetype = movetype
        self.movecategory = movecategory
        self.effects = effects
        self.name = name
        if currentpp == 'max':
            self.currentpp = pp
        else:
            self.currentpp = currentpp
        
    def executemove(self, user, target):
        self.currentpp -= 1
        if type(self.accuracy) == float:
            if not random.randint(0, 100) in range(0, int(self.accuracy * 100) + 1):
                return 'miss', None, None
        
        # all options for move execution effects
        damage = 0
        typeeffectiveness = 1.0
        if self.damage > 0:
            damage = int((((2 * user.level / 5 + 2) * self.damage * (user.getatk() / target.getdef())) / 50) + 2)
            stab = 1.5 if self.movetype in (dex()[user.dexno]['type1'], dex()[user.dexno]['type2']) else 1.0
            typeeffectiveness = typechart.check_effectiveness(self, target)
            damage = int(damage * stab * typeeffectiveness)
            target.changehp(damage)
        else:
            damage = 0
            typeeffectiveness = None
        if 'selfraisestat' in self.effects:
            stat = self.effects['selfraisestat'][0]
            stages = self.effects['selfraisestat'][1]
            user.raisestat(stat, stages)
        if 'chanceselfraisestat' in self.effects:
            stat = self.effects['chanceselfraisestat'][0]
            stages = self.effects['chanceselfraisestat'][1]
            if random.randing(0, 100) < (self.effects['chanceselfraisestat'][2] * 100):
                user.raisestat(stat, stages)
        if 'enemyraisestat' in self.effects:
            stat = self.effects['enemyraisestat'][0]
            stages = self.effects['enemyraisestat'][1]
            target.raisestat(stat, stages)
        if 'chanceenemyraisestat' in self.effects:
            stat = self.effects['chanceenemyraisestat'][0]
            stages = self.effects['chanceenemyraisestat'][1]
            if random.randint(0, 100) < (self.effects['chanceenemyraisestat'][2] * 100):
                target.raisestat(stat, stages)
        

        return 'hit', damage, typeeffectiveness
    
    def restorepp(self, amount):
        if self.currentpp + amount > self.pp:
            self.currentpp = self.pp
        elif self.currentpp + amount < 0:
            self.currentpp = 0
        else:
            self.currentpp = self.currentpp + amount