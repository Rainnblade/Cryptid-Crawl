''' this will be for the damage calculation function when i decide to look it in its devilish face at some
point this week

moves (move, power (_/100), accuracy (_/100), uses_max (how much to reset to at the end of fight),
        uses_temp (use during combat, duration (how long a spell lasts), type (physical or elemental)

- shield works like detect from pokemon where it reflects everything until that pokemon's next turn
- combat has to be kept track of in terms of how many rounds have passed for rage and maybe others
- lay on hands heals a target for a certain amount of  (that 25 is healing a target for a quarter of their health no matter their max)
- fog cloud brings up general evasion for target
-last stand works the same as blood right but the character' health needs to be witin the last like 5th or something (in the red)
- chill touch has an increased crit chance
- guidance makes the target's next move a sure fire hit (smart players would use it on the jersey devil and then chill touch
- maybe add a thing that flurry of blows can hit multiple times or somethin so it can do more damage
- shocking grasp can cause the target to be paralyzed for their next move
- intimidate does the same thing as shocking grasp but doesnt do damage and has a greater chance to hit
- longstrider decreases the accuracy of the next move against it (makes them harder to hit)
- stuff hurts more if the person has a hunter's mark and the attacker has the move in their set (blood hunter and ranger)

- a status effect if it lasts for 1 turn goes away the person is effected by it
'''
from characters import *
import random

def damage_calc_player(guy,angy_enemy,move):
    '''this function will include the damage calculations and the applying of modifiers
    critical hit is a 1/16 chance (1 for no crit and 2 for yes crit)
    chance to hit is done first which is random number between 0 and 100 and the move hits if its under the accuracy threshold of the move
    if the move hits is another random number between 0 and 100
    find the modifier first or kind of move so entangle isnt too hard of a look up'''
    for i in characters[guy]['moves']:
        if i[0] == move:
            guy_acc = i[2]

    if move=='blood rite' and enemies[angy_enemy]['effect'] !='marked':
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

    damage = ((((2*2*crit_chance/5)+ 2) * guy_pow * guy_attack/angy_def)/50)+2

    if move=='shield':
        characters[guy]['effect'] = 'shielded'
    elif characters[guy]['effect'] == 'shielded':
        damage = 0

    if move=='entangle':
        enemies[angy_enemy]['effect'] = 'entangled'

    if move=='fog cloud':
        enemies[angy_enemy]['effect'] = 'clouded'

    if move=='Hunter mark':
        enemies[angy_enemy]['effect'] = 'marked'

    if random.randrange(1, 101) > guy_acc:
        return 'missed'
    else:
        return round(damage)

def damage_calc_enemy(attacker,defender,move):
    '''this function will include the damage calculations and the applying of modifiers
    critical hit is a 1/16 chance (1 for no crit and 2 for yes crit)
    chance to hit is done first which is random number between 0 and 100 and the move hits if its under the accuracy threshold of the move
    if the move hits is another random number between 0 and 100
    find the modifier first or kind of move so entangle isnt too hard of a look up'''
    for i in enemies[attacker]['moves']:
        if i[0] == move:
            attacker_acc = i[2]
            if enemies[attacker]['effect'] == 'entangled' and i[-1] == 'physical':
                return f"{attacker} is stuck and can't move"

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

    if move == 'pack support':
        pass

    if random.randrange(1,101) > attacker_acc:
        return 'missed'
    else:
        return round(damage)

def update_stat(guy,num,stat,heal:False):
    if (isinstance(num,int) == False and isinstance(num,float) == False) or (isinstance(num, str) and num.isdigit() == False):
        print(f'digit was a word: {num}')
        return False
    if guy in enemies:
        if heal == False:
            enemies[guy][stat] -=  int(num)
    elif guy in characters:
        if heal == False:
            characters[guy][stat] -= int(num)

    print('update_stat finished')

def turn_order(roster):
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
    '''resets temp health and move use numbers at the end of a dungeon'''
    if guy in enemies:
        enemies[guy]['temp_health'] = enemies[guy]['health']
    elif guy in characters:
        characters[guy]['temp_health'] = characters[guy]['health']
        for i in characters[guy]['moves']:
            i[4] = i[3]
    print('reset finished')
