from classes.dex import get_dex as dex
from classes import pokemon
from classes import moves

type_chart = {
    'Normal': {'weak': [], 'resist': ['Ghost'], 'immune': ['Ghost']},
    'Fire': {'weak': ['Water', 'Ground', 'Rock'], 'resist': ['Fire', 'Grass', 'Ice', 'Bug'], 'immune': []},
    'Water': {'weak': ['Electric', 'Grass'], 'resist': ['Fire', 'Water', 'Ice'], 'immune': []},
    'Electric': {'weak': ['Ground'], 'resist': ['Electric', 'Flying', 'Steel'], 'immune': []},
    'Grass': {'weak': ['Fire', 'Ice', 'Poison', 'Flying', 'Bug'], 'resist': ['Water', 'Electric', 'Grass', 'Ground'], 'immune': []},
    'Ice': {'weak': ['Fire', 'Fighting', 'Rock', 'Steel'], 'resist': ['Ice'], 'immune': []},
    'Fighting': {'weak': ['Flying', 'Psychic', 'Fairy'], 'resist': ['Bug', 'Rock', 'Dark'], 'immune': []},
    'Poison': {'weak': ['Ground', 'Psychic'], 'resist': ['Grass', 'Fighting', 'Poison', 'Bug'], 'immune': []},
    'Ground': {'weak': ['Water', 'Grass', 'Ice'], 'resist': ['Poison', 'Rock'], 'immune': ['Electric']},
    'Flying': {'weak': ['Electric', 'Ice', 'Rock'], 'resist': ['Grass', 'Fighting', 'Bug'], 'immune': ['Ground']},
    'Psychic': {'weak': ['Bug', 'Ghost', 'Dark'], 'resist': ['Fighting', 'Psychic'], 'immune': []},
    'Bug': {'weak': ['Fire', 'Flying', 'Rock'], 'resist': ['Grass', 'Fighting', 'Ground'], 'immune': []},
    'Rock': {'weak': ['Water', 'Grass', 'Fighting', 'Ground', 'Steel'], 'resist': ['Normal', 'Fire', 'Poison', 'Flying'], 'immune': []},
    'Ghost': {'weak': ['Ghost', 'Dark'], 'resist': ['Poison', 'Bug'], 'immune': ['Normal', 'Fighting']},
    'Dragon': {'weak': ['Ice', 'Dragon', 'Fairy'], 'resist': ['Fire', 'Water', 'Electric', 'Grass'], 'immune': []},
    'Dark': {'weak': ['Fighting', 'Bug', 'Fairy'], 'resist': ['Ghost', 'Dark'], 'immune': ['Psychic']},
    'Steel': {'weak': ['Fire', 'Fighting', 'Ground'], 'resist': ['Normal', 'Grass', 'Ice', 'Flying', 'Psychic', 'Bug', 'Rock', 'Dragon', 'Steel', 'Fairy'], 'immune': ['Poison']},
    'Fairy': {'weak': ['Poison', 'Steel'], 'resist': ['Fighting', 'Bug', 'Dark'], 'immune': ['Dragon']}
}


def check_effectiveness(move, defender):
    move_type = move.movetype
    defender_types = [dex()[defender.dexno]['type1'], dex()[defender.dexno]['type2']]

    effectiveness = 1.0
    for dtype in defender_types:
        if dtype is not 'None':
            if move_type in type_chart[dtype]['weak']:
                effectiveness *= 2
            elif move_type in type_chart[dtype]['resist']:
                effectiveness *= 0.5
            elif move_type in type_chart[dtype]['immune']:
                effectiveness *= 0
    return effectiveness