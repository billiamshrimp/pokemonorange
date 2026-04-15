inside:[true or false depending on whether the map is somewhere inside]
objects:[nps, items, and other interactables (or simply none): object_type,x,y,data.data.data...|object_type,x,y,data.data.data...]
warps:[x,y,destination,targetx,targety|x,y,destination,targetx,targety (such that (0,0) is top left and bottom right is (>0,>0))]
connections:[direction,destination,offset_from_zero]
wild:[encounter_type,minlevel,maxlevel,species.species.species(...)|encounter_type,minlevel,maxlevel,species.species.species(...)]
conditions:[naturalweather|naturalfield]
configuration:[nothing goes here]
[array of numbers separated by commas. the numbers represent the number tile to use. You can add spaces to align them more gridlike]

Objects Elaborated:
if facing direction is none, the trainer must be spoken to. moveset changes and item is allowed to be none.
trainers: [trainer,x,y,facing_direction.skin.name.level-pokemon_id-item-moveset_changes.level-pokemon_id-item-moveset_changes...]
items: [item,x,y,item_id.item_type]