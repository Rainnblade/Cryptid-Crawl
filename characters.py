"""
This file exists to store all the base stats and moves of player and enemy characters
"""

"""
dictionary containing all player character stat blocks

format
name: name of character
    health: base health of enemy
    temp_health: the health manipulated in game through battle and items
    defense: defense used in battle calculations (out of 20)
    attack: attack power of character used in battle calculations
    speed: speed used to determine turn order when combat starts
    moves (move, power (_/100), accuracy (_/100), uses_max (how much to reset to at the end of fight),
            uses_temp (use during combat), duration (how long a spell lasts), type (physical or elemental): the list
            of moves a character can do in battle
    effect: location for effects to be applied for future move calculations if they apply"""
characters = {
    'Bigfoot':{
        'health':25,
        'temp_health':25,
        'defense':15,
        'attack':12,
        'speed':22,
        'moves':[['axe swing',70,80,10,10,0,'physical'],['rage',0,100,2,2,2,'physical'],['punch',60,70,15,15,0,'physical']],
        'effect':None
    },
    'Mothman':{
        'health':14,
        'temp_health':14,
        'defense':13,
        'attack':6,
        'speed':19,
        'moves':[['shield',0,100,15,15,1,'physical'],['magic missile',50,90,20,20,0,'physical'],['fire bolt',80,70,15,15,0,'fire'],['poison spray',60,80,10,10,0,'poison']],
        'effect':None
    },
    'Jersey Devil':{
        'health':20,
        'temp_health':20,
        'defense':11,
        'attack':10,
        'speed':20,
        'moves':[['chill touch',90,60,5,5,0,'necrotic'],['smite',90,80,10,10,0,'physical'],['lay on hands',25,100,5,5,0,'physical'],['sickle swipe',70,70,20,20,0,'physical']],
        'effect':None
    },
    'Selkie':{
        'health':21,
        'temp_health':21,
        'defense':14,
        'attack':8,
        'speed':30,
        'moves':[['ice knife',70,100,10,10,0,'frost'],['magic stones',50,60,20,20,0,'physical'],['entangle',0,100,10,10,1,'physical'],['fog cloud',0,100,10,10,1,'physical']],
        'effect':None
    },
    'Chupakabra':{
        'health':20,
        'temp_health':20,
        'defense':13,
        'attack':10,
        'speed':21,
        'moves':[['Hunter mark',0,100,20,20,1,'physical'],['blood rite',80,100,15,15,0,'necrotic'],['drain',50,50,10,10,0,'physical'],['last stand',90,100,5,5,0,'physical']],
        'effect':None
    },
    'SCP Deer':{
        'health':19,
        'temp_health':19,
        'defense':13,
        'attack':8,
        'speed':25,
        'moves':[['vicious mockery',60,70,70,15,15,0,'physical'],['dissonant whispers',80,60,60,10,10,0,'physical'],['longstrider',0,100,15,15,0,'physical'],['starry wisps',70,75,15,15,0,'lightning']],
        'effect':None
    },
    'Frogman':{
        'health':17,
        'temp_health':17,
        'defense':13,
        'attack':8,
        'speed':25,
        'moves':[['dagger',60,80,15,15,0,'physical'],['crossbow',80,60,20,20,0,'physical'],['decoy',0,80,15,15,1,'physical'],['sneak attack',90,100,15,15,0,'physical']],
        'effect':None
    },
    'Jackalope':{
        'health':17,
        'temp_health':17,
        'defense':11,
        'attack':8,
        'speed':28,
        'moves':[['cure wounds',0,100,20,20,0,'physical'],['spare the dying',0,50,5,5,0,'physical'],['guidance',0,50,5,5,0,'physical'],['sacred flame',60,70,20,20,0,'fire']],
        'effect':None
    },
    'Ogua':{
        'health':24,
        'temp_health':24,
        'defense':15,
        'attack':10,
        'speed':22,
        'moves':[['bash',60,80,20,20,0,'physical'],['cure wounds',0,100,15,15,0,'physical'],['hunter mark',0,100,20,20,0,'physical'],['flatten',90,60,10,10,0,'physical']],
        'effect':None
    },
    'Wendigo':{
        'health':19,
        'temp_health':19,
        'defense':14,
        'attack':8,
        'speed':34,
        'moves':[['cold breath',70,80,10,10,0,'frost'],['flurry of blows',60,90,15,15,0,'physical'],['shocking grasp',70,90,20,20,0,'lightning'],['intimidate',0,70,10,10,0,'physical']],
        'effect':None
    }
}

"""
dictionary for all enemy character stat blocks
possible enemies
    - bear
    - humans 
    - humans with armor
    - humans with gun
    - rabid dogs
    - badger
    - coyotes
    - goat
    - big ass rat

format
name: name of character
    health: base health of enemy
    temp_health: the health manipulated in game through battle and items
    defense: defense used in battle calculations (out of 20)
    attack: attack power of character used in battle calculations
    speed: speed used to determine turn order when combat starts
    moves (move, power (_/100), accuracy (_/100), duration (how long a spell lasts), type (physical or elemental): the list
            of moves a character can do in battle
    effect: location for effects to be applied for future move calculations if they apply
"""

enemies = {
    'Bear':{
        'health':34,
        'temp_health':34,
        'defense':11,
        'attack':12,
        'speed':30,
        'moves':[['bite',70,80,0,'physical'],['claws',60,90,0,'physical']],
        'effect':None
    },
    'Human':{
        'health':4,
        'temp_health':4,
        'defense':10,
        'attack':4,
        'speed':20,
        'moves':[['bat',60,70,0,'physical'],['first aid',0,100,1,'physical']],
        'effect':None
    },
    'Coyote':{
        'health':7,
        'temp_health':7,
        'defense':13,
        'attack':8,
        'speed':28,
        'moves':[['bite',60,80,0,'physical'],['pack support',0,100,0,'physical']],
        'effect':None
    },
    'Human with gun':{
        'health':9,
        'temp_health':9,
        'defense':9,
        'attack':12,
        'speed':19,
        'moves':[['gun',80,70,1,'bleed'],['melee',60,80,0,'physical']],
        'effect':None
    }
}
