"""
This script creates a basic RPG framework with four game states:
- START: Displays a start screen
- CHARACTER_SELECT: Grid-based party selection screen (choose 3 of 5 cryptids)
- MAP: Shows a grid-based map where the player can move (player is currently displayed as a white square.)
- MINIMAP: Displays a mini map when M is pressed
- BATTLE: Displays a battle screen. Can be triggered by pressing B on a red battle tile

Controls:
- ENTER: Start the game / select or deselect a character
- SPACE: Confirm party selection (when 3 are chosen)
- WASD: Navigate character select grid / move player on the map
- M: Open minimap
- B: Enter battle (when standing on a red battle tile)
- 1-4: Select a move during battle
- ESC: Return to map (from battle or minimap)
"""
# Imports
import pygame
import sys
import random
from characters import characters, enemies
from combat_state import damage_calc_player, damage_calc_enemy, turn_order, update_stat


pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cryptid Crawl")

clock = pygame.time.Clock()

# Sprites for character select, eventually combat?
_mothman_raw = pygame.image.load('sprites/mothman.png').convert()
sprites = {
    'Mothman': pygame.transform.scale(_mothman_raw, (130, 130))
}

# Game states
START = "start"
CHARACTER_SELECT = "character_select"
MAP = "map"
MINIMAP = "minimap"
BATTLE = "battle"

state = START

# Character select
ROSTER = ['Bigfoot', 'Mothman', 'Jersey Devil', 'Selkie', 'Chupakabra']
select_index = 0
party = []

# Player
player_pos = [5, 5]

# Map settings
TILE_SIZE = 50
MAP_WIDTH = 10
MAP_HEIGHT = 10

font = pygame.font.SysFont(None, 48)

# Create map grid
game_map = [[0 for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

# Battle tile — red dot on the map where the Bear battle is.
BATTLE_TILE = [3, 3]
bear_defeated = False # Bear starts alive.

# Combat state
combat_enemy = 'Bear'
combat_enemy_hp = 0
combat_order = []
combat_turn_idx = 0
combat_log = []
combat_phase = 'player_choose'  # 'player_choose', 'win', 'lose'
combat_menu = 'main'            # 'main', 'moves', 'info'



def start_combat(enemy_name):
    """
    Initiates combat against the given enemy and begin the first turn.

    Sets up turn order using speed values, resets the enemy's HP, and
    automatically performs the first turn if it belongs to the enemy.
    """
    global combat_enemy, combat_enemy_hp, combat_order, combat_turn_idx, combat_log, combat_phase
    combat_enemy = enemy_name
    combat_enemy_hp = enemies[enemy_name]['health']
    roster = [enemy_name] + list(party)
    combat_order = turn_order(roster)
    combat_turn_idx = -1
    combat_log = [f"A hostile {enemy_name} appeared!"]
    combat_phase = 'player_choose'
    _next_turn()


def _next_turn():
    """
    Advances to the next alive party member's turn.

    Enemy turns are performed automatically. Stops when it reaches a living
    party member (sets phase to 'player_choose') or sets phase to 'lose'
    if all party members HP is dropped to 0.

    To be used with start_combat()/do_player_move()
    """
    global combat_turn_idx, combat_phase, combat_menu

    for _ in range(len(combat_order) + 1):
        combat_turn_idx = (combat_turn_idx + 1) % len(combat_order)
        current = combat_order[combat_turn_idx]

        if current == combat_enemy:
            if combat_enemy_hp > 0:
                _do_enemy_action()
                if all(characters[p]['temp_health'] <= 0 for p in party):
                    combat_phase = 'lose'
                    return
        else:
            if characters[current]['temp_health'] > 0:
                combat_phase = 'player_choose'
                combat_menu = 'main'
                return

    combat_phase = 'lose'


def _do_enemy_action():
    """
    Resolves the enemy's turn by picking a random move in their moveset and applying damage
    to a randomly chosen party member.

    To be used with _next_turn()
    """
    move_name = random.choice(enemies[combat_enemy]['moves'])[0]
    targets = [p for p in party if characters[p]['temp_health'] > 0]
    if not targets:
        return
    target = random.choice(targets)

    result = damage_calc_enemy(combat_enemy, target, move_name)

    if isinstance(result, int):
        update_stat(target, result, 'temp_health', False)
        combat_log.append(f"{combat_enemy} used {move_name}!")
        combat_log.append(f"{target} took {result} damage.")
    elif result == 'missed':
        combat_log.append(f"{combat_enemy} used {move_name} — missed!")
    else:
        combat_log.append(str(result))

    if len(combat_log) > 8: # Caps combat log at 8 entries, can be changed.
        combat_log.pop(0)


def do_player_move(move_name):
    """
    Performs the player's selected move and then advances the turn.

    Handles hit/miss/special results from damage_calc_player and checks for
    enemy defeat after applying damage. Currently only the bear enemy is being tracked.
    """
    global combat_enemy_hp, combat_phase, bear_defeated

    current = combat_order[combat_turn_idx]
    result = damage_calc_player(current, combat_enemy, move_name)

    if isinstance(result, int):
        combat_enemy_hp -= result
        combat_log.append(f"{current} used {move_name}!")
        combat_log.append(f"{combat_enemy} took {result} damage.")
        if combat_enemy_hp <= 0:
            combat_enemy_hp = 0
            combat_log.append(f"{combat_enemy} was defeated!")
            combat_phase = 'win'
            bear_defeated = True
            return
    elif result == 'missed':
        combat_log.append(f"{current} used {move_name} — missed!")
    else:
        combat_log.append(str(result))

    if len(combat_log) > 8:
        combat_log.pop(0)

    _next_turn()


# Draw Start Screen
def draw_start():
    """
    Render the start screen.

    Fills the screen with a dark background and displays
    a centered message prompting the user to press ENTER to begin the game.
    """

    screen.fill((30, 30, 30))

    title = font.render("Press ENTER to Start", True, (255,255,255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2))


# Draw Character Select Screen
def draw_character_select():
    """
    Render the character select screen.

    Displays a grid of 5 (currently) character boxes where the player can browse and select
    a party of 3 cryptids. Use WASD to navigate the boxes, ENTER to select or deselect a character into your party,
    and SPACE to confirm when 3 have been chosen.
    """
    screen.fill((20, 20, 20))

    small_font = pygame.font.SysFont(None, 30)
    name_font = pygame.font.SysFont(None, 26)

    title = font.render("Choose Your Characters", True, (220, 220, 220))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    BOX_SIZE = 130
    GAP = 18

    row1_y = 90
    row2_y = row1_y + BOX_SIZE + GAP + 20  # +20 for name label below box

    row1_x = WIDTH//2 - (3*BOX_SIZE + 2*GAP)//2
    row2_x = WIDTH//2 - (2*BOX_SIZE + GAP)//2

    positions = [
        (row1_x + 0*(BOX_SIZE+GAP), row1_y),
        (row1_x + 1*(BOX_SIZE+GAP), row1_y),
        (row1_x + 2*(BOX_SIZE+GAP), row1_y),
        (row2_x + 0*(BOX_SIZE+GAP), row2_y),
        (row2_x + 1*(BOX_SIZE+GAP), row2_y),
    ]

    for i, name in enumerate(ROSTER):
        x, y = positions[i]

        border_color = (220, 220, 220) if i == select_index else (60, 60, 60)
        border_width = 3 if i == select_index else 1

        # Use sprite if available, otherwise draw placeholder box
        if name in sprites:
            screen.blit(sprites[name], (x, y))
        else:
            pygame.draw.rect(screen, (45, 45, 45), (x, y, BOX_SIZE, BOX_SIZE))
            placeholder = name_font.render(name, True, (90, 90, 90))
            screen.blit(placeholder, (x + BOX_SIZE//2 - placeholder.get_width()//2, y + BOX_SIZE//2 - placeholder.get_height()//2))

        pygame.draw.rect(screen, border_color, (x, y, BOX_SIZE, BOX_SIZE), border_width)

        # Party slot badge in top-left corner
        if name in party:
            slot = party.index(name) + 1
            pygame.draw.rect(screen, (80, 80, 80), (x+2, y+2, 24, 24))
            slot_surf = small_font.render(str(slot), True, (255, 255, 255))
            screen.blit(slot_surf, (x+5, y+4))

        # Name below box
        name_color = (255, 255, 255) if name in party else (160, 160, 160)
        name_surf = name_font.render(name, True, name_color)
        screen.blit(name_surf, (x + BOX_SIZE//2 - name_surf.get_width()//2, y + BOX_SIZE + 5))

    party_text = small_font.render(f"Party: {len(party)} / 3", True, (180, 180, 180))
    screen.blit(party_text, (WIDTH//2 - party_text.get_width()//2, row2_y + BOX_SIZE + 35))

    if len(party) == 3:
        confirm = small_font.render("SPACE to confirm  |  ENTER to deselect", True, (220, 220, 220))
        screen.blit(confirm, (WIDTH//2 - confirm.get_width()//2, row2_y + BOX_SIZE + 65))
    else:
        hint = small_font.render("ENTER to select/deselect", True, (80, 80, 80))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, row2_y + BOX_SIZE + 65))


# Draw Main Map
def draw_map():
    """
    Render the map screen.

    Draws a grid-based map using TILE_SIZE, MAP_WIDTH, and MAP_HEIGHT.
    Each tile is outlined for visibility. A red tile marks the Bear encounter
    spot. The player is rendered as a white square at the current player_pos.
    """

    screen.fill((30, 30, 30))

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):

            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(screen, (80, 80, 80), rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Draws red dot battle tile if bear hasn't been defeated
    if not bear_defeated:
        bx = BATTLE_TILE[0] * TILE_SIZE
        by = BATTLE_TILE[1] * TILE_SIZE
        pygame.draw.rect(screen, (160, 30, 30), (bx, by, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, (0, 0, 0), (bx, by, TILE_SIZE, TILE_SIZE), 1)
        dot_font = pygame.font.SysFont(None, 22)
        dot_label = dot_font.render("B", True, (255, 180, 180))
        screen.blit(dot_label, (bx + TILE_SIZE//2 - dot_label.get_width()//2,
                                 by + TILE_SIZE//2 - dot_label.get_height()//2))

    # Draw player
    px = player_pos[0]*TILE_SIZE
    py = player_pos[1]*TILE_SIZE

    pygame.draw.rect(screen, (220, 220, 220), (px,py,TILE_SIZE,TILE_SIZE))

    draw_party_panel()

# Draw Party Panel (right sidebar on map screen)
def draw_party_panel():
    """
    Render the party panel on the right side of the map screen.

    Displays each party member's name, current HP, and a health bar.
    This pulls live stat data from the characters dictionary.
    """
    # Panel Size
    panel_x = MAP_WIDTH * TILE_SIZE  # 500
    panel_width = WIDTH - panel_x    # 300

    panel_font = pygame.font.SysFont(None, 26) # Character Name Font Size
    label_font = pygame.font.SysFont(None, 22) # HP Label Font Size

    # Panel background
    pygame.draw.rect(screen, (15, 15, 15), (panel_x, 0, panel_width, HEIGHT))
    pygame.draw.line(screen, (60, 60, 60), (panel_x, 0), (panel_x, HEIGHT), 2)

    title = panel_font.render("Party", True, (200, 200, 200))
    screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, 10)) # Positioning of text

    SLOT_HEIGHT = 80
    for i, name in enumerate(party): # Numbers each character name and indexes them.
        slot_y = 40 + i * (SLOT_HEIGHT + 10)

        stats = characters.get(name, {})
        hp_max = stats.get('health', 1)
        hp_cur = stats.get('temp_health', hp_max)

        # Slot background
        pygame.draw.rect(screen, (30, 30, 30), (panel_x + 10, slot_y, panel_width - 20, SLOT_HEIGHT))
        pygame.draw.rect(screen, (60, 60, 60), (panel_x + 10, slot_y, panel_width - 20, SLOT_HEIGHT), 1)

        # Slot number + name
        slot_label = panel_font.render(f"{i+1}. {name}", True, (220, 220, 220))
        screen.blit(slot_label, (panel_x + 16, slot_y + 8))

        # HP text
        hp_text = label_font.render(f"HP: {hp_cur} / {hp_max}", True, (160, 160, 160))
        screen.blit(hp_text, (panel_x + 16, slot_y + 32))

        # HP bar
        bar_x = panel_x + 16
        bar_y = slot_y + 52
        bar_w = panel_width - 32
        bar_h = 12
        ratio = hp_cur / hp_max if hp_max > 0 else 0

        if ratio > 0.5:
            bar_color = (60, 180, 60)
        elif ratio > 0.25:
            bar_color = (200, 160, 40)
        else:
            bar_color = (180, 50, 50)

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), 1)


# Draw Battle Screen
def draw_battle():
    """
    Render the battle screen.

    Left area displays enemy name and HP bar, combat log, and move selection menu
    for the active party member. Right area of GUI displays party panel showing live HP.
    Number keys 1-4 to select option and moves. ESC to return map after a win or loss.
    """
    screen.fill((20, 20, 20))

    combat_font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 26)
    tiny_font = pygame.font.SysFont(None, 22)

    # Enemy Area of screen
    enemy_max_hp = enemies[combat_enemy]['health']

    enemy_label = combat_font.render(combat_enemy, True, (220, 80, 80))
    screen.blit(enemy_label, (30, 25))

    bar_x, bar_y, bar_w, bar_h = 30, 65, 320, 16
    ratio = max(0, combat_enemy_hp / enemy_max_hp)
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, (180, 50, 50), (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), 1)

    hp_text = small_font.render(f"HP: {max(0, combat_enemy_hp)} / {enemy_max_hp}", True, (160, 160, 160))
    screen.blit(hp_text, (bar_x, bar_y + 22))

    # Combat log
    log_x, log_y, log_w, log_h = 30, 120, 450, 170
    pygame.draw.rect(screen, (28, 28, 28), (log_x, log_y, log_w, log_h))
    pygame.draw.rect(screen, (60, 60, 60), (log_x, log_y, log_w, log_h), 1)

    for i, msg in enumerate(combat_log[-5:]):
        msg_surf = tiny_font.render(msg, True, (200, 200, 200))
        screen.blit(msg_surf, (log_x + 8, log_y + 8 + i * 30))

    # Different states of the combat menu
    if combat_phase == 'player_choose':
        current = combat_order[combat_turn_idx]
        moves = characters[current]['moves']

        turn_label = small_font.render(f"{current}'s turn:", True, (220, 220, 100))
        screen.blit(turn_label, (30, 310))

        COL_NAME = 30
        COL_PWR  = 220
        COL_USES = 280
        COL_TYPE = 340

        if combat_menu == 'main':
            btn1 = small_font.render("1.  Moves", True, (200, 200, 200))
            btn2 = small_font.render("2.  Move Info", True, (200, 200, 200))
            btn3 = small_font.render("3.  Flee", True, (200, 200, 200))
            screen.blit(btn1, (30, 350))
            screen.blit(btn2, (30, 385))
            screen.blit(btn3, (30, 420))

        elif combat_menu == 'moves':
            for i, move in enumerate(moves):
                col = i % 2
                row = i // 2
                move_surf = small_font.render(f"{i+1}. {move[0]}", True, (200, 200, 200))
                screen.blit(move_surf, (30 + col * 230, 350 + row * 34))
            back = tiny_font.render("B — back", True, (100, 100, 100))
            screen.blit(back, (30, 460))

        elif combat_menu == 'info':
            # Header — each label drawn at its fixed column x
            screen.blit(tiny_font.render("Move", True, (140, 140, 140)), (COL_NAME, 345))
            screen.blit(tiny_font.render("Pwr",  True, (140, 140, 140)), (COL_PWR,  345))
            screen.blit(tiny_font.render("Uses", True, (140, 140, 140)), (COL_USES, 345))
            screen.blit(tiny_font.render("Type", True, (140, 140, 140)), (COL_TYPE, 345))
            pygame.draw.line(screen, (60, 60, 60), (30, 362), (460, 362), 1)

            for i, move in enumerate(moves):
                # move format: [name, power, accuracy, uses_max, uses_temp, duration, type]
                row_y = 368 + i * 26
                screen.blit(tiny_font.render(f"{i+1}. {move[0]}", True, (200, 200, 200)), (COL_NAME, row_y))
                screen.blit(tiny_font.render(str(move[1]), True, (200, 200, 200)),         (COL_PWR,  row_y))
                screen.blit(tiny_font.render(str(move[4]), True, (200, 200, 200)),         (COL_USES, row_y))
                screen.blit(tiny_font.render(move[6],      True, (200, 200, 200)),         (COL_TYPE, row_y))

            back = tiny_font.render("B — back", True, (100, 100, 100))
            screen.blit(back, (30, 460))

    elif combat_phase == 'win':
        win_surf = combat_font.render("Victory!", True, (100, 220, 100))
        screen.blit(win_surf, (30, 320))
        hint = small_font.render("Press ESC to return to map", True, (160, 160, 160))
        screen.blit(hint, (30, 365))

    elif combat_phase == 'lose':
        lose_surf = combat_font.render("Defeated...", True, (220, 80, 80))
        screen.blit(lose_surf, (30, 320))
        hint = small_font.render("Press ESC to return to map", True, (160, 160, 160))
        screen.blit(hint, (30, 365))

    # Party panel
    draw_party_panel()


# Draw Mini Map
def draw_minimap():
    """
    Render the minimap screen.

    Displays a grid view of the full map centered on the screen,
    with the player's current position marked. Also shows the current area name.
    Press ESC to close and return to the map.
    Will include surrounding areas soon.
    """
    screen.fill((20,20,20))

    mini_tile = 20

    map_width_px = MAP_WIDTH * mini_tile
    map_height_px = MAP_HEIGHT * mini_tile

    start_x = WIDTH//2 - map_width_px//2
    start_y = HEIGHT//2 - map_height_px//2

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):

            rect = pygame.Rect(
                start_x + x*mini_tile,
                start_y + y*mini_tile,
                mini_tile,
                mini_tile
            )

            pygame.draw.rect(screen,(60,60,60),rect)
            pygame.draw.rect(screen,(0,0,0),rect,1)

    # Battle tile marker on minimap
    if not bear_defeated:
        bx = start_x + BATTLE_TILE[0] * mini_tile
        by = start_y + BATTLE_TILE[1] * mini_tile
        pygame.draw.rect(screen, (160, 30, 30), (bx, by, mini_tile, mini_tile))

    # Player marker
    px = start_x + player_pos[0]*mini_tile
    py = start_y + player_pos[1]*mini_tile

    pygame.draw.rect(screen,(220,220,220),(px,py,mini_tile,mini_tile))

    area_name = pygame.font.SysFont(None, 40).render("Area Name", True, (255, 220, 150))
    screen.blit(area_name, (WIDTH//2 - area_name.get_width()//2, 60))

    text = pygame.font.SysFont(None,32).render("Press ESC to close map",True,(255,255,255))
    screen.blit(text,(WIDTH//2-text.get_width()//2,100))


# Game loop
if __name__ == "__main__":
 while True:
    """
    Main game loop.

    Handles:
    - Event processing (quit, key presses)
    - Game state transitions
    - Player movement and boundary constraints
    - Rendering the appropriate screen based on current state
    """


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # START screen
            if state == START:
                if event.key == pygame.K_RETURN:
                    state = CHARACTER_SELECT

            # CHARACTER SELECT controls
            elif state == CHARACTER_SELECT:
                if event.key == pygame.K_a:
                    select_index = (select_index - 1) % len(ROSTER)
                if event.key == pygame.K_d:
                    select_index = (select_index + 1) % len(ROSTER)
                if event.key == pygame.K_w:
                    if select_index >= 3:
                        select_index -= 3
                if event.key == pygame.K_s:
                    if select_index < 3:
                        select_index = min(select_index + 3, len(ROSTER) - 1)
                if event.key == pygame.K_RETURN:
                    name = ROSTER[select_index]
                    if name in party:
                        party.remove(name)
                    elif len(party) < 3:
                        party.append(name)
                if event.key == pygame.K_SPACE:
                    if len(party) == 3:
                        state = MAP

            # MAP controls
            elif state == MAP:

                if event.key == pygame.K_m:
                    state = MINIMAP
                if event.key == pygame.K_b:
                    if player_pos == BATTLE_TILE and not bear_defeated:
                        start_combat('Bear')
                        state = BATTLE

                if event.key == pygame.K_w:
                    player_pos[1] -= 1

                if event.key == pygame.K_s:
                    player_pos[1] += 1

                if event.key == pygame.K_a:
                    player_pos[0] -= 1

                if event.key == pygame.K_d:
                    player_pos[0] += 1

                # Keep player inside map
                player_pos[0] = max(0, min(MAP_WIDTH-1, player_pos[0]))
                player_pos[1] = max(0, min(MAP_HEIGHT-1, player_pos[1]))

            # BATTLE controls
            elif state == BATTLE:
                if event.key == pygame.K_ESCAPE:
                    state = MAP

                if combat_phase == 'player_choose':
                    current = combat_order[combat_turn_idx]
                    moves = characters[current]['moves']

                    if combat_menu == 'main':
                        if event.key == pygame.K_1:
                            combat_menu = 'moves'
                        elif event.key == pygame.K_2:
                            combat_menu = 'info'
                        elif event.key == pygame.K_3:
                            state = MAP

                    elif combat_menu == 'moves':
                        if event.key == pygame.K_b:
                            combat_menu = 'main'
                        else:
                            move_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                            for i, key in enumerate(move_keys):
                                if event.key == key and i < len(moves):
                                    do_player_move(moves[i][0])
                                    break

                    elif combat_menu == 'info':
                        if event.key == pygame.K_b:
                            combat_menu = 'main'

            # MINIMAP controls
            elif state == MINIMAP:
                if event.key == pygame.K_ESCAPE:
                    state = MAP


    # Draw screens
    if state == START:
        draw_start()

    elif state == CHARACTER_SELECT:
        draw_character_select()

    elif state == MAP:
        draw_map()

    elif state == BATTLE:
        draw_battle()

    elif state == MINIMAP:
        draw_minimap()

    pygame.display.flip()
    clock.tick(60)
