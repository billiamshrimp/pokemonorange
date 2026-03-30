# -*- coding: utf-8 -*-
"""
Everything ever needed in battle in one place!
"""

import pygame
import math
import random

import abilities
import moves
from dex import dex

weathermessages = {'none': 'There is no weather',
                   'sun': 'The harsh sun beams down',
                   'rain': 'The rain pours down',
                   'sand': 'The sandstorm rages',
                   'snow': 'The snow falls'}
terrainmessages = {'none': 'There is no special terrain',
                   'grass': 'The terrain is grassy and full of life',
                   'psychic': 'The terrain warps and distorts',
                   'electric': 'The terrain buzzes with electricity',
                   'dust': 'The terrain is barren and raw'}
tilesize = 64
turn = 1
turnstate = ['battlestart']
abilitycondition = ['none']
damagevariables = {
    'useattackanddefense': True,
    'physical': True,
    'uselevel': False,
    'weatherboost': False,
    'weatherdiminish': False,
    'critical': False,
    'userandom': True,
    'STAB': False,
    'stabdamage': 1.5,
    'statushinder': False,
    'usestagemods': True,
    'stagemod': 1,
    'extramods': 1,
    'contact': False,
    'blocked': False,
    'percentbased': False,
    'percentmod': 1,
    }
playerparty = {}
playeractivemember = [1]
enemyparty = {}
enemyactivemember = [1]
sprites = {}
stageimage = {}
prioritybrackets = [5, 4, 3, 2, 1, 0, -3, -4, -5, -6, -7]
playerstages = {
    'atk': 6,
    'def': 6,
    'spa': 6,
    'spd': 6,
    'spe': 6,
    }
enemystages = {
    'atk': 6,
    'def': 6,
    'spa': 6,
    'spd': 6,
    'spe': 6,
    }
stages = [1/4, 2/7, 2/6, 2/5, 2/4, 2/3, 1, 3/2, 2, 5/2, 3, 7/2, 4]
weather = ['none', 5]
field = ['none', 5]
battletype = ['wild']

battlemenulayer = ['default']
selecterposition = [[375, 435], [625, 435], [375, 535], [625, 535]]
optionselect = [0]

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


def enterBattle(fieldimage, battletype_, playerparty_, enemyparty_, weatherr='none', fieldd='none'):
    #Setup images
    sprites['player'] = pygame.transform.scale(
        pygame.image.load(playerparty_[1].sprite).convert(), (192, 192)
        )
    sprites['enemy'] = pygame.transform.scale(
        pygame.image.load(enemyparty_[1].sprite).convert(), (192, 192)
        )
    for i in playerparty_:
        playerparty[i] = playerparty_[i]
    for i in enemyparty_:
        enemyparty[i] = enemyparty_[i]
    
    battletype[0] = battletype_
    
    if fieldimage == 'default':
        stageimage[0] = pygame.transform.scale(
            pygame.image.load("graphics/battlefields/default.png").convert(), (832, 640)
            )
    setweather(weatherr)
    setfield(fieldd)
    
    checkandapplyability(playerparty[1], enemyparty[1], 'entersbattle')
    
    turnstate[0] = 'moveselect'
    
def setweather(weather_):
    weather[0] = weather_

def clearweather():
    weather[0] = 'none'

def setfield(field_):
    field[0] = field_
    
def clearfield():
    field[0] = 'none'
    
def checkandapplyability(playermon, enemymon, turnstage_ = turnstate[0]):
    if playermon.getspe() >= enemymon.getspe():
        if playermon.getability().checkactivation(turnstage_, abilitycondition):
            playermon.getability().executeability(playermon, enemymon, 'player')
        if enemymon.getability().checkactivation(turnstage_, abilitycondition):
            enemymon.getability().executeability(playermon, enemymon, 'enemy')
    else:
        if enemymon.getability().checkactivation(turnstage_, abilitycondition):
            enemymon.getability().executeability(playermon, enemymon, 'enemy')
        if playermon.getability().checkactivation(turnstage_, abilitycondition):
            playermon.getability().executeability(playermon, enemymon, 'player')    

def checksingleability(mons, turnstage_ = turnstate[0]):
    for mon in mons:
        if mon.getability().checkactivation(turnstage_, abilitycondition):
            if mon == playerparty[playeractivemember[0]]:
                mon.getability().executeability(playerparty[playeractivemember[0]], enemyparty[enemyactivemember[0]], 'player')
            else:
                mon.getability().executeability(playerparty[playeractivemember[0]], enemyparty[enemyactivemember[0]], 'enemy')

def setdamagevariables(cause):
    pass

def calcanddodamage(user, target):
    pass

def getstagemod(pokemon, stat):
    if pokemon == 'player':
        return playerstages[stat]
    else:
        return enemystages[stat]

def playerallowselection(battletype_, gamefont, gamefontsmall, surface):
    options = [0,0,0,0]
    selecter = pygame.transform.scale(pygame.image.load("graphics/ui/overworldselecter.png").convert(), (50, 50))
    if battlemenulayer[0] == 'default':
        options[0] = gamefont.render("Fight", False, (0, 0, 0))
        options[1] = gamefont.render("Bag", False, (0, 0, 0))
        options[2] = gamefont.render("Pokemon", False, (0, 0, 0))
        options[3] = gamefont.render("Run", False, (0, 0, 0))
    elif battlemenulayer[0] == 'moves':
        options[0] = gamefontsmall.render(playerparty[playeractivemember[0]].moves[1].name, False, (0, 0, 0))
        options[1] = gamefontsmall.render(playerparty[playeractivemember[0]].moves[2].name, False, (0, 0, 0))
        options[2] = gamefontsmall.render(playerparty[playeractivemember[0]].moves[3].name, False, (0, 0, 0))
        options[3] = gamefontsmall.render(playerparty[playeractivemember[0]].moves[4].name, False, (0, 0, 0))
    surface.blit(options[0], [420, 430])
    surface.blit(options[1], [670, 430])
    surface.blit(options[2], [420, 530])
    surface.blit(options[3], [670, 530])
    if waskeypressed(pygame.K_DOWN):
        optionselect[0] = (optionselect[0] + 2) % 4
    elif waskeypressed(pygame.K_UP):
        optionselect[0] = (optionselect[0] - 2) % 4
    elif waskeypressed(pygame.K_LEFT):
        optionselect[0] = (optionselect[0] - 1) % 4
    elif waskeypressed(pygame.K_RIGHT):
        optionselect[0] = (optionselect[0] + 1) % 4
    elif waskeypressed(pygame.K_z):
        if battlemenulayer[0] == 'default':
            if optionselect[0] == 0:
                battlemenulayer[0] = 'moves'
            elif optionselect[0] == 1:
                pass #bag/inventory
            elif optionselect[0] == 2:
                pass #party
            elif optionselect[0] == 3:
                return 'overworld'
        elif battlemenulayer[0] == 'moves':
            playermove_ = (playerparty[playeractivemember[0]].moves[(optionselect[0] +1)] if len(playerparty[playeractivemember[0]].moves) >= (optionselect[0] +1) else playerparty[playeractivemember[0]].moves[len(playerparty[playeractivemember[0]].moves)])
            enemymove_ = decideenemymove(playerparty[playeractivemember[0]], enemyparty[enemyactivemember[0]], (playerparty[playeractivemember[0]].moves[(optionselect[0] +1)] if len(playerparty[playeractivemember[0]].moves) >= (optionselect[0] +1) else playerparty[playeractivemember[0]].moves[len(playerparty[playeractivemember[0]].moves)]))
            print(playerparty[playeractivemember[0]], enemyparty[enemyactivemember[0]], playermove_, enemymove_)
            executeturn(playerparty[playeractivemember[0]], enemyparty[enemyactivemember[0]], playermove_, enemymove_)
            
    elif waskeypressed(pygame.K_x):
        if battlemenulayer[0] == 'moves':
            battlemenulayer[0] = 'default'
        
    surface.blit(selecter, selecterposition[optionselect[0]])
    return 'battle'
    
def changestage(pokemon, stat, modifier):
    if pokemon == 'player':
        playerstages[stat] += modifier
        if playerstages[stat] > 12:
            playerstages[stat] = 12
        elif playerstages[stat] < 0:
            playerstages[stat] = 0
    else:
        enemystages[stat] += modifier
        if enemystages[stat] > 12:
            enemystages[stat] = 12
        elif enemystages[stat] < 0:
            enemystages[stat] = 0

def executeturn(playermon, enemymon, playermove, enemymove):
    for priority_ in prioritybrackets:
        if playermove[0].priority == priority_ and enemymove[0].priority == priority_:
            if playermon.getspe(stages[playerstages['spe']]) > enemymon.getspe(stages[enemystages['spe']]):
                playermove[0].executemove(playermove[1])
                enemymove[0].executemove(enemymove[1])
            elif playermon.getspe(stages[playerstages['spe']]) < enemymon.getspe(stages[enemystages['spe']]):
                enemymove[0].executemove(enemymove[1])
                playermove[0].executemove(playermove[1])
            else:
                if random.randint(0,1) == 1:
                    playermove[0].executemove(playermove[1])
                    enemymove[0].executemove(enemymove[1])
                else:
                    enemymove[0].executemove(enemymove[1])
                    playermove[0].executemove(playermove[1])
        elif playermove[0].priority == priority_:
            playermove[0].executemove(playermove[1])
        elif enemymove[0].priority == priority_:
            enemymove[0].executemove(enemymove[1])

    if weather[0] != 'none':
        weather[1] -= 1
        if weather[1] == 0:
            clearweather()
            weather[1] = 5
    
    if field[0] != 'none':
        field[1] -= 1
        if field[1] == 0:
            clearfield()
            field[1] = 5

def decideenemymove(playermon, enemymon, playermove):
    if battletype[0] == 'wild':
        return enemymon.moves[random.randint(1, len(enemymon.moves))]

def draw(surface):
    surface.blit(stageimage[0], (0,0))
    surface.blit(sprites['player'], (120, 174))
    surface.blit(sprites['enemy'], (500, 50))
    

