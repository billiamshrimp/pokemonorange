# -*- coding: utf-8 -*-
"""
Move Data and execution
"""
import random

import pokemon
import battlescript as b


moves = {
    'Tackle': [40, 35, 0, 1.0, 'Normal', 'Physical', {'contact'}, 'Tackle'],
    'Howl': [0, 40, 0, 'cannotmiss', 'Normal', 'Status', {'selfraisestat' : ['atk', 1]}, 'Howl'],
    'Rock Throw': [50, 15, 0, 0.9, 'Rock', 'Physical', {}, 'Rock Throw'],
    'Rock Polish': [0, 20, 0, 'cannotmiss', 'Rock', 'Status', {'selfraisestat': ['spe', 2]}, 'Rock Polish'],
    'Rock Tomb': [60, 15, 0, 0.95, 'Rock', 'Physical', {'enemyraisestat': ['spe', -1]}, 'Rock Tomb']
    }
# Establishes a Move with effects being a set of string keywords
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
        
    def executemove(self, user, targets):
        b.checkandapplyability(b.playerparty[b.playeractivemember[0]], b.enemyparty[b.enemyactivemember[0]], 'moveused')
        if type(self.accuracy) == float:
            if random.randint(0, 100) in range(0, self.accuracy * 100 + 1):
                b.checkandapplyability(b.playerparty[b.playeractivemember[0]], b.enemyparty[b.enemyactivemember[0]], 'movewillhit')
                if self.damage != 0:
                    for target in targets:
                        b.calcanddodamage(user, target)
                for effect in self.effects:
                    if effect == 'contact': 
                        b.checksingleability(targets, 'contact')
                    elif effect == 'selfraisestat':
                        b.chagestage(user, self.effects['selfraisestat'][0], self.effects['selfraisestat'][1])
                    elif effect == 'enemyraisestat':
                        for target in targets:
                            b.changestage(target, self.effects['enemyraisestat'][0], self.effects['enemyraisestat'][1])
                    
                    
            else:
                return 'miss'
        else:
            b.checkandapplyability(b.playerparty[b.playeractivemember[0]], b.enemyparty[b.enemyactivemember[0]], 'movewillhit')
            return 'hit'
    
    def restorepp(self, amount):
        if self.currentpp + amount > self.pp:
            self.currentpp = self.pp
        elif self.currentpp + amount < 0:
            self.currentpp = 0
        else:
            self.currentpp = self.currentpp + amount