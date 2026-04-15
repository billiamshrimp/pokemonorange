def get_events_for_stage(stage_id):
    pass

def get_dialogue_for_npc(npc_name, dialogue_number):
    with open(f"resources/data/npc_dialogue.dat") as file:
        lines = file.read().splitlines()
    for i in range(len(lines)):
        line = lines[i].split(':')
        if line[0] == npc_name:
            return line[1].split('.')[dialogue_number]
    return 'no dialogue found'
