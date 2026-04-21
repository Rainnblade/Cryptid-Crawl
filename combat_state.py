'''
This script includes all the functions that run in the background of the combat screen to do things like generate the
order of characters involved, the amount of damage done by moves, and the reset of character stats when the game
session is over
'''

from characters import *
import random

def damage_calc_player(guy,angy_enemy,move):
    '''
    Calculates the number of damage done or healed by characters in the player's control with modifiers applied depending
    on the selected moves type or the effect currently assigned to the character doing the attack

    inputs
     - guy: player character doing the attack
     - angy_enemy: the enemy character getting attacked or the teammate being healed
     - move: the move the player character is doing

    returns
     - damage: number calculated through speed, attack, defence, and accuracy stats as well as effects/modifiers
     - other: if the move misses due to accuracy stat,the function will return that the move missed or failed
    '''
    for i in characters[guy]['moves']:
        if i[0] == move:
            guy_acc = i[2]

    if angy_enemy in characters:
        if move == 'lay on hands':
            damage = int(characters[angy_enemy]['health'] * 0.5)
            return round(damage)

    if move=='blood rite' and enemies[angy_enemy]['effect'] !='marked':
        guy_acc = 50

    if move == 'last stand' and (enemies[angy_enemy]['temp_health'] > int(enemies[angy_enemy]['health'] * 0.2)):
        guy_acc = 50

    if move=='decoy':
        characters[guy]['effect'] = 'hidden'
    elif characters[guy]['effect'] != 'hidden' and move == 'sneak attack':
        return f"failed because {guy} isn't hidden"

    guy_attack = characters[guy]['attack']
    angy_def = enemies[angy_enemy]['defense']
    guy_pow = 0
    if random.randrange(1,17) == 16:
        crit_chance = 2
    else:
        crit_chance = 1

    for i in characters[guy]['moves']:
        if i[0] == move:
            guy_pow = i[1]

    if move == 'chill touch':
        if random.randrange(1,5) == 4:
            crit_chance = 2
        else:
            crit_chance = 1


    damage = ((((2*2*crit_chance/5)+ 2) * guy_pow * guy_attack/angy_def)/50)+2

    if move=='shield':
        characters[guy]['effect'] = 'shielded'

    if move=='entangle':
        enemies[angy_enemy]['effect'] = 'entangled'

    if move=='fog cloud':
        enemies[angy_enemy]['effect'] = 'clouded'

    if move=='Hunter mark':
        enemies[angy_enemy]['effect'] = 'marked'

    if move == 'guidance':
        characters[angy_enemy]['effect'] = 'guided'
    elif characters[guy]['effect'] == 'guided':
        guy_acc = 1

    if move == 'shocking grasp':
        enemies[angy_enemy]['effect'] = 'paralyzed'
        damage = damage * 1.5

    if move == 'rage':
        characters[guy]['effect'] = 'enraged'
    elif characters[guy]['effect'] == 'enraged':
        damage = damage * 1.5

    if move == 'intimidate':
         enemies[angy_enemy]['effect'] = 'intimidated'

    if move == 'longstrider':
        characters[guy]['effect'] = 'striding'

    for i in characters[guy]['moves']:
        if i[0] == move:
            if i[-1] == 'fire':
                damage = damage * 1.5
            elif i[-1] == 'poison':
                damage = damage * 1.4
            elif i[-1] == 'necrotic':
                damage = damage * 1.6
            elif i[-1] == 'frost':
                damage = damage * 1.2
            elif i[-1] == 'lightning':
                damage = damage * 1.5

    if random.randrange(1, 101) > guy_acc:
        return 'missed'
    else:
        return round(damage)

def damage_calc_enemy(attacker,defender,move):
    '''
    Calculates the number of damage done or healed by enemies with modifiers applied depending
    on the selected moves type or the effect currently assigned to the character doing the attack

    inputs
     - attacker: enemy character doing the attack
     - defender: the player character getting attacked or the teammate being healed
     - move: the move the enemy character is doing

    returns
     - damage: number calculated through speed, attack, defence, and accuracy stats as well as effects/modifiers
     - other: if the move misses due to accuracy stat,the function will return that the move missed or failed
    '''
    for i in enemies[attacker]['moves']:
        if i[0] == move:
            attacker_acc = i[2]
            if enemies[attacker]['effect'] == 'entangled' and i[-1] == 'physical':
                return f"{attacker} is stuck and can't move"

    if defender in enemies:
        if move == 'first aid':
            damage = int(enemies[defender]['health'] * 0.25)
            return round(damage)

        if move == 'pack support':
            damage = int(enemies[defender]['health'] * 0.25)
            return round(damage)
            
    attacker_attack = enemies[attacker]['attack']
    defender_def = characters[defender]['defense']
    attacker_pow = 0
    if random.randrange(1,17) == 16:
        crit_chance = 2
    else:
        crit_chance = 1

    for i in enemies[attacker]['moves']:
        if i[0] == move:
            attacker_pow = i[1]

    damage = ((((2*2*crit_chance/5)+ 2) * attacker_pow * attacker_attack/defender_def)/50)+2


    if enemies[attacker]['effect'] == 'clouded':
        attacker_acc -= 30
        enemies[attacker]['effect'] = None

    if enemies[attacker]['effect'] == 'paralyzed':
        enemies[attacker]['effect'] = None
        return f"{attacker} couldn't move due to paralysis"

    if characters[defender]['effect'] == 'shielded':
        characters[defender]['effect'] = None
        return f'{defender} was protected with shield'

    if enemies[attacker]['effect'] == 'intimidated':
        enemies[attacker]['effect'] = None
        return f'{attacker} is intimidated and cannot move'

    if characters[defender]['effect'] == 'striding':
        attacker_acc -= 30
        characters[defender]['effect'] = None

    for i in enemies[attacker]['moves']:
        if i[0] == move:
            if i[-1] == 'bleed':
                damage = damage * 1.7

    if random.randrange(1,101) > attacker_acc:
        return 'missed'
    else:
        return round(damage)

def update_stat(guy,num,stat,heal):
    """
    changes stat that is given
    if that stat is health being healed or taken away and the end result is outside ths parameter of 0 to the character's
    max health then it sets that stat to the necessary low or the necessary high

    inputs
     - guy: enemy or player character being effected
     - num: number being subtracted or added
     - stat: the stat on the character being affected
     - heal: true or false depending on if the stat is being changed due to damage taken or healing given

    return
     - if the output from the damage calc isn't a number, it returns False.
     - If the output from the damage calc requires a change, the change is carried out and it returns nothing
    """
    if isinstance(num,int) == False and isinstance(num,float) == False:
        return False
    if guy in enemies:
        if heal == False:
            enemies[guy][stat] -=  int(num)
        else:
            enemies[guy][stat] += int(num)

        if enemies[guy]['temp_health'] < 0:
            enemies[guy]['temp_health'] = 0
        elif enemies[guy]['temp_health'] > enemies[guy]['health']:
            enemies[guy]['temp_health'] = enemies[guy]['health']

    elif guy in characters:
        if heal == False:
            characters[guy][stat] -= int(num)
        else:
            characters[guy][stat] += int(num)

        if characters[guy]['temp_health'] < 0:
            characters[guy]['temp_health'] = 0
        elif characters[guy]['temp_health'] > characters[guy]['health']:
            characters[guy]['temp_health'] = characters[guy]['health']

def turn_order(roster):
    """
    compares the speed stat of everyone given in the roster and sorts them from fastest to slowest

    input
     - roster: array of characters that are involved in the battle

    return
     - the sorted array in order of fastest to slowest for battle initiative order
    """
    temp = []
    while len(roster) != 0:
        max_speed = 0
        for i in roster:
            if i in enemies:
                if enemies[i]['speed'] > max_speed:
                    max_speed = enemies[i]['speed']
            elif i in characters:
                if characters[i]['speed'] > max_speed:
                    max_speed = characters[i]['speed']

        for i in roster:
            if i in enemies:
                if enemies[i]['speed'] == max_speed:
                    temp.append(i)
                    roster.remove(i)
            elif i in characters:
                if characters[i]['speed'] == max_speed:
                    temp.append(i)
                    roster.remove(i)

    return temp


def reset(guy):
    '''
    resets temp health and move use numbers at the end of a dungeon

    input
     - guy: character being effected

     return
     - noting
    '''
    if guy in enemies:
        enemies[guy]['temp_health'] = enemies[guy]['health']
    elif guy in characters:
        characters[guy]['temp_health'] = characters[guy]['health']
        for i in characters[guy]['moves']:
            i[4] = i[3]

