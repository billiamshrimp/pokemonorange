# -*- coding: utf-8 -*-
"""
Manages abilities
"""
import pokemon
from dex import dex
import battlescript

# {abilityname: [activationtime, activationcondition, flavortext]}
abilities = {
    'Adaptability': ['dealdamage', 'dealdamage',
                     'This Pokemon does more damage when attacking with moves of its own type'
                     ],
    'Magic Guard': ['takedamage', 'takedamage',
                    'This Pokemon can only take direct damage'
                    ],
    'Adaptive Shielding': ['entersbattle', 'entersbattle',
                           'This Pokemon has its defensive stats boosted adaptively on entry'
                           ],
    }

def buildability(name):
    return ability(abilities[name][0], abilities[name][1], name)

class ability:
    def __init__(self, activationtime, activationcondition, name):
        self.activationtime = activationtime
        self.activationcondition = activationcondition
        self.name = name
        
    def checkactivation(self, battletime, condition):
        return battletime == self.activationtime and condition == self.activationcondition
    
    #this is the coding for every single ability all in one place and easy to add more
    def executeability(self, playermon, enemymon, user):
        if self.name == 'Adaptability':
            battlescript.damagevariables['stabdamage'] = 2
            
        if self.name == 'Magic Guard':
            pass
        
        if self.name == 'Adaptive Shielding':
            if user == 'player':
                if enemymon.getatk(battlescript.getstagemod(user, 'atk')) >= enemymon.getspa(battlescript.getstagemod(user, 'spa')):
                    battlescript.changestage(user, 'def', 1)
                else:
                    battlescript.changestage(user, 'spd', 1)
            else:
                if playermon.getatk(battlescript.getstagemod(user, 'atk')) >= playermon.getspa(battlescript.getstagemod(user, 'spa')):
                    battlescript.changestage(user, 'def', 1)
                else:
                    battlescript.changestage(user, 'spd', 1)