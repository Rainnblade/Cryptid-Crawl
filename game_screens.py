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
import sys
import random
import pygame
from characters import characters, enemies
from combat_state import damage_calc_player, damage_calc_enemy, turn_order, update_stat


pygame.init()

# Window setup
#: Window width in pixels.
_WIDTH = 800
#: Window height in pixels.
_HEIGHT = 600
#: The main pygame display surface.
_screen = pygame.display.set_mode((_WIDTH, _HEIGHT))
pygame.display.set_caption("Cryptid Crawl")

#: Pygame clock used to cap the frame rate at 60 FPS.
_clock = pygame.time.Clock()

# Sprites for character select, eventually combat?

_mothman_raw = pygame.image.load('sprites/mothman.png').convert()
_jersey_devil_raw = pygame.image.load('sprites/jersey_devil.png').convert()
_chupacabra_raw = pygame.image.load('sprites/chupacabra.png').convert()
_ogua_raw = pygame.image.load('sprites/ogua.png').convert()
_bigfoot_raw = pygame.image.load('sprites/bigfoot.png').convert()
_selkie_raw = pygame.image.load('sprites/selkie.png').convert()
#: Scaled sprite surfaces keyed by character name (130x130 px).
_sprites = {
    'Mothman': pygame.transform.scale(_mothman_raw, (130, 130)),
    'Jersey Devil': pygame.transform.scale(_jersey_devil_raw, (130, 130)),
    'Chupakabra': pygame.transform.scale(_chupacabra_raw, (130, 130)),
    'Ogua': pygame.transform.scale(_ogua_raw, (130, 130)),
    'Bigfoot': pygame.transform.scale(_bigfoot_raw, (130, 130)),
    'Selkie': pygame.transform.scale(_selkie_raw, (130, 130)),
}

# Game states
#: Game state constant: start screen.
_START = "start"
#: Game state constant: character selection screen.
_CHARACTER_SELECT = "character_select"
#: Game state constant: main map view.
_MAP = "map"
#: Game state constant: minimap overlay.
_MINIMAP = "minimap"
#: Game state constant: battle screen.
_BATTLE = "battle"

#: Current game state; controls which screen is rendered each frame.
_state = _START

# Character select
#: Names of all selectable cryptid characters shown on the character select screen.
_ROSTER = ['Bigfoot', 'Mothman', 'Jersey Devil', 'Selkie', 'Chupakabra', 'Ogua']
#: Index into _ROSTER of the currently highlighted character box.
_select_index = 0
#: List of up to 3 selected character names forming the player's party.
_party = []

# Player
#: Player's current [x, y] tile position on the map.
_player_pos = [5, 5]

# Map settings
#: Pixel size of each map tile.
_TILE_SIZE = 50
#: Number of tile columns in the map grid.
_MAP_WIDTH = 10
#: Number of tile rows in the map grid.
_MAP_HEIGHT = 10

#: Default system font at size 48 for primary UI text.
_font = pygame.font.SysFont(None, 48)

# Create map grid
#: 2D grid representing the map; each cell defaults to 0 (empty tile).
_game_map = [[0 for x in range(_MAP_WIDTH)] for y in range(_MAP_HEIGHT)]

# Choose random spawn locations for enemies
def _pick_enemy_tiles():
    """Picks a random non-overlapping spawn tile for each enemy, avoiding where the player starts."""
    avoid_spawn = {(5, 5)}
    candidates = [(x, y) for x in range(_MAP_WIDTH) for y in range(_MAP_HEIGHT) if (x, y) not in avoid_spawn]
    chosen = random.sample(candidates, 2)
    return {'Bear': list(chosen[0]), 'Coyote': list(chosen[1])}

#: Maps each enemy name to its [x, y] spawn tile on the map.
_enemy_tiles = _pick_enemy_tiles()
#: Set of enemy names that have been defeated this run.
_defeated_enemies = set()

# Combat state
#: Name of the enemy currently being fought.
_combat_enemy = 'Bear'
#: Enemy's remaining HP during the current battle.
_combat_enemy_hp = 0
#: Turn order list (character names sorted by speed) for the current battle.
_combat_order = []
#: Index into _combat_order indicating whose turn it currently is.
_combat_turn_idx = 0
#: Rolling list of recent combat messages displayed on the battle screen.
_combat_log = []
#: Current combat phase: ``'player_choose'``, ``'win'``, or ``'lose'``.
_combat_phase = 'player_choose'
#: Active combat submenu: ``'main'``, ``'moves'``, or ``'info'``.
_combat_menu = 'main'



def start_combat(enemy_name):
    """
    Initiates combat against the given enemy and begin the first turn.

    Sets up turn order using speed values, resets the enemy's HP, and
    automatically performs the first turn if it belongs to the enemy.
    """
    global _combat_enemy, _combat_enemy_hp, _combat_order, _combat_turn_idx, _combat_log, _combat_phase
    _combat_enemy = enemy_name
    _combat_enemy_hp = enemies[enemy_name]['health']
    roster = [enemy_name] + list(_party)
    _combat_order = turn_order(roster)
    _combat_turn_idx = -1
    _combat_log = [f"A hostile {enemy_name} appeared!"]
    _combat_phase = 'player_choose'
    _next_turn()


def _next_turn():
    """
    Advances to the next alive party member's turn.

    Enemy turns are performed automatically. Stops when it reaches a living
    party member (sets phase to 'player_choose') or sets phase to 'lose'
    if all party members HP is dropped to 0.

    To be used with start_combat()/do_player_move()
    """
    global _combat_turn_idx, _combat_phase, _combat_menu

    for _ in range(len(_combat_order) + 1):
        _combat_turn_idx = (_combat_turn_idx + 1) % len(_combat_order)
        current = _combat_order[_combat_turn_idx]

        if current == _combat_enemy:
            if _combat_enemy_hp > 0:
                _do_enemy_action()
                if all(characters[p]['temp_health'] <= 0 for p in _party):
                    _combat_phase = 'lose'
                    return
        else:
            if characters[current]['temp_health'] > 0:
                _combat_phase = 'player_choose'
                _combat_menu = 'main'
                return

    _combat_phase = 'lose'


def _do_enemy_action():
    """
    Resolves the enemy's turn by picking a random move in their moveset and applying damage
    to a randomly chosen party member.

    To be used with _next_turn()
    """
    move_name = random.choice(enemies[_combat_enemy]['moves'])[0]
    targets = [p for p in _party if characters[p]['temp_health'] > 0]
    if not targets:
        return
    target = random.choice(targets)

    result = damage_calc_enemy(_combat_enemy, target, move_name)

    if isinstance(result, int):
        update_stat(target, result, 'temp_health', False)
        _combat_log.append(f"{_combat_enemy} used {move_name}!")
        _combat_log.append(f"{target} took {result} damage.")
    elif result == 'missed':
        _combat_log.append(f"{_combat_enemy} used {move_name} — missed!")
    else:
        _combat_log.append(str(result))

    if len(_combat_log) > 8: # Caps combat log at 8 entries, can be changed.
        _combat_log.pop(0)


def do_player_move(move_name):
    """
    Performs the player's selected move and then advances the turn.

    Handles hit/miss/special results from damage_calc_player and checks for
    enemy defeat after applying damage.
    """
    global _combat_enemy_hp, _combat_phase

    current = _combat_order[_combat_turn_idx]
    result = damage_calc_player(current, _combat_enemy, move_name)

    if isinstance(result, int):
        _combat_enemy_hp -= result
        _combat_log.append(f"{current} used {move_name}!")
        _combat_log.append(f"{_combat_enemy} took {result} damage.")
        if _combat_enemy_hp <= 0:
            _combat_enemy_hp = 0
            _combat_log.append(f"{_combat_enemy} was defeated!")
            _combat_phase = 'win'
            _defeated_enemies.add(_combat_enemy)
            return
    elif result == 'missed':
        _combat_log.append(f"{current} used {move_name} — missed!")
    else:
        _combat_log.append(str(result))

    if len(_combat_log) > 8:
        _combat_log.pop(0)

    _next_turn()


# Draw Start Screen
def draw_start():
    """
    Render the start screen.

    Fills the screen with a dark background and displays
    a centered message prompting the user to press ENTER to begin the game.
    """

    _screen.fill((30, 30, 30))

    title = _font.render("Press ENTER to Start", True, (255,255,255))
    _screen.blit(title, (_WIDTH//2 - title.get_width()//2, _HEIGHT//2))


# Draw Character Select Screen
def draw_character_select():
    """
    Render the character select screen.

    Displays a grid of 6 (currently) character boxes where the player can browse and select
    a party of 3 cryptids. Use WASD to navigate the boxes, ENTER to select or deselect a character into your party,
    and SPACE to confirm when 3 have been chosen.
    """
    _screen.fill((20, 20, 20))

    small_font = pygame.font.SysFont(None, 30)
    name_font = pygame.font.SysFont(None, 26)

    title = _font.render("Choose Your Characters", True, (220, 220, 220))
    _screen.blit(title, (_WIDTH//2 - title.get_width()//2, 20))

    BOX_SIZE = 130
    GAP = 18

    row1_y = 90
    row2_y = row1_y + BOX_SIZE + GAP + 20  # +20 for name label below box

    row1_x = _WIDTH//2 - (3*BOX_SIZE + 2*GAP)//2

    positions = [
        (row1_x + 0*(BOX_SIZE+GAP), row1_y),
        (row1_x + 1*(BOX_SIZE+GAP), row1_y),
        (row1_x + 2*(BOX_SIZE+GAP), row1_y),
        (row1_x + 0*(BOX_SIZE+GAP), row2_y),
        (row1_x + 1*(BOX_SIZE+GAP), row2_y),
        (row1_x + 2*(BOX_SIZE+GAP), row2_y),
    ]

    for i, name in enumerate(_ROSTER):
        x, y = positions[i]

        border_color = (212, 175, 55) if i == _select_index else (60, 60, 60) # Character Selection Border
        border_width = 6 if i == _select_index else 1

        # Use sprite if available, otherwise draw placeholder box
        if name in _sprites:
            _screen.blit(_sprites[name], (x, y))
        else:
            pygame.draw.rect(_screen, (45, 45, 45), (x, y, BOX_SIZE, BOX_SIZE))
            placeholder = name_font.render(name, True, (90, 90, 90))
            _screen.blit(placeholder, (x + BOX_SIZE//2 - placeholder.get_width()//2, y + BOX_SIZE//2 - placeholder.get_height()//2))

        pygame.draw.rect(_screen, border_color, (x, y, BOX_SIZE, BOX_SIZE), border_width)

        # Party slot badge in top-left corner
        if name in _party:
            slot = _party.index(name) + 1
            pygame.draw.rect(_screen, (80, 80, 80), (x+2, y+2, 24, 24))
            slot_surf = small_font.render(str(slot), True, (255, 255, 255))
            _screen.blit(slot_surf, (x+5, y+4))

        # Name below box
        name_color = (255, 255, 255) if name in _party else (160, 160, 160)
        name_surf = name_font.render(name, True, name_color)
        _screen.blit(name_surf, (x + BOX_SIZE//2 - name_surf.get_width()//2, y + BOX_SIZE + 5))

    party_text = small_font.render(f"Party: {len(_party)} / 3", True, (180, 180, 180))
    _screen.blit(party_text, (_WIDTH//2 - party_text.get_width()//2, row2_y + BOX_SIZE + 35))

    if len(_party) == 3:
        confirm = small_font.render("SPACE to confirm  |  ENTER to deselect", True, (220, 220, 220))
        _screen.blit(confirm, (_WIDTH//2 - confirm.get_width()//2, row2_y + BOX_SIZE + 65))
    else:
        hint = small_font.render("ENTER to select/deselect", True, (80, 80, 80))
        _screen.blit(hint, (_WIDTH//2 - hint.get_width()//2, row2_y + BOX_SIZE + 65))


# Draw Main Map
def draw_map():
    """
    Render the map screen.

    Draws a grid-based map using _TILE_SIZE, _MAP_WIDTH, and _MAP_HEIGHT.
    Each tile is outlined for visibility. Red tiles mark enemy encounter spots.
    The player is rendered as a white square at the current _player_pos.
    """

    _screen.fill((30, 30, 30))

    for y in range(_MAP_HEIGHT):
        for x in range(_MAP_WIDTH):

            rect = pygame.Rect(x*_TILE_SIZE, y*_TILE_SIZE, _TILE_SIZE, _TILE_SIZE)

            pygame.draw.rect(_screen, (80, 80, 80), rect)
            pygame.draw.rect(_screen, (0,0,0), rect, 1)

    # Draws enemy tiles for undefeated enemies
    dot_font = pygame.font.SysFont(None, 22)
    for enemy_name, tile in _enemy_tiles.items():
        if enemy_name not in _defeated_enemies:
            bx = tile[0] * _TILE_SIZE
            by = tile[1] * _TILE_SIZE
            pygame.draw.rect(_screen, (160, 30, 30), (bx, by, _TILE_SIZE, _TILE_SIZE))
            pygame.draw.rect(_screen, (0, 0, 0), (bx, by, _TILE_SIZE, _TILE_SIZE), 1)
            dot_label = dot_font.render(enemy_name[0], True, (255, 180, 180))
            _screen.blit(dot_label, (bx + _TILE_SIZE//2 - dot_label.get_width()//2,
                                     by + _TILE_SIZE//2 - dot_label.get_height()//2))

    # Draw player
    px = _player_pos[0]*_TILE_SIZE
    py = _player_pos[1]*_TILE_SIZE

    pygame.draw.rect(_screen, (220, 220, 220), (px,py,_TILE_SIZE,_TILE_SIZE))

    draw_party_panel()

# Draw Party Panel (right sidebar on map screen)
def draw_party_panel():
    """
    Render the party panel on the right side of the map screen.

    Displays each party member's name, current HP, and a health bar.
    This pulls live stat data from the characters dictionary.
    """
    # Panel Size
    panel_x = _MAP_WIDTH * _TILE_SIZE  # 500
    panel_width = _WIDTH - panel_x    # 300

    panel_font = pygame.font.SysFont(None, 26) # Character Name Font Size
    label_font = pygame.font.SysFont(None, 22) # HP Label Font Size

    # Panel background
    pygame.draw.rect(_screen, (15, 15, 15), (panel_x, 0, panel_width, _HEIGHT))
    pygame.draw.line(_screen, (60, 60, 60), (panel_x, 0), (panel_x, _HEIGHT), 2)

    title = panel_font.render("Party", True, (200, 200, 200))
    _screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, 10)) # Positioning of text

    SLOT_HEIGHT = 80
    for i, name in enumerate(_party): # Numbers each character name and indexes them.
        slot_y = 40 + i * (SLOT_HEIGHT + 10)

        stats = characters.get(name, {})
        hp_max = stats.get('health', 1)
        hp_cur = stats.get('temp_health', hp_max)

        # Slot background
        pygame.draw.rect(_screen, (30, 30, 30), (panel_x + 10, slot_y, panel_width - 20, SLOT_HEIGHT))
        pygame.draw.rect(_screen, (60, 60, 60), (panel_x + 10, slot_y, panel_width - 20, SLOT_HEIGHT), 1)

        # Slot number + name
        slot_label = panel_font.render(f"{i+1}. {name}", True, (220, 220, 220))
        _screen.blit(slot_label, (panel_x + 16, slot_y + 8))

        # HP text
        hp_text = label_font.render(f"HP: {hp_cur} / {hp_max}", True, (160, 160, 160))
        _screen.blit(hp_text, (panel_x + 16, slot_y + 32))

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

        pygame.draw.rect(_screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(_screen, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(_screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), 1)


# Draw Battle Screen
def draw_battle():
    """
    Render the battle screen.

    Left area displays enemy name and HP bar, combat log, and move selection menu
    for the active party member. Right area of GUI displays party panel showing live HP.
    Number keys 1-4 to select option and moves. ESC to return map after a win or loss.
    """
    _screen.fill((20, 20, 20))

    combat_font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 26)
    tiny_font = pygame.font.SysFont(None, 22)

    # Enemy Area of screen
    enemy_max_hp = enemies[_combat_enemy]['health']

    enemy_label = combat_font.render(_combat_enemy, True, (220, 80, 80))
    _screen.blit(enemy_label, (30, 25))

    bar_x, bar_y, bar_w, bar_h = 30, 65, 320, 16
    ratio = max(0, _combat_enemy_hp / enemy_max_hp)
    pygame.draw.rect(_screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(_screen, (180, 50, 50), (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(_screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), 1)

    hp_text = small_font.render(f"HP: {max(0, _combat_enemy_hp)} / {enemy_max_hp}", True, (160, 160, 160))
    _screen.blit(hp_text, (bar_x, bar_y + 22))

    # Combat log
    log_x, log_y, log_w, log_h = 30, 120, 450, 170
    pygame.draw.rect(_screen, (28, 28, 28), (log_x, log_y, log_w, log_h))
    pygame.draw.rect(_screen, (60, 60, 60), (log_x, log_y, log_w, log_h), 1)

    for i, msg in enumerate(_combat_log[-5:]):
        msg_surf = tiny_font.render(msg, True, (200, 200, 200))
        _screen.blit(msg_surf, (log_x + 8, log_y + 8 + i * 30))

    # Different states of the combat menu
    if _combat_phase == 'player_choose':
        current = _combat_order[_combat_turn_idx]
        moves = characters[current]['moves']

        turn_label = small_font.render(f"{current}'s turn:", True, (220, 220, 100))
        _screen.blit(turn_label, (30, 310))

        COL_NAME = 30
        COL_PWR  = 220
        COL_USES = 280
        COL_TYPE = 340

        if _combat_menu == 'main':
            btn1 = small_font.render("1.  Moves", True, (200, 200, 200))
            btn2 = small_font.render("2.  Move Info", True, (200, 200, 200))
            btn3 = small_font.render("3.  Flee", True, (200, 200, 200))
            _screen.blit(btn1, (30, 350))
            _screen.blit(btn2, (30, 385))
            _screen.blit(btn3, (30, 420))

        elif _combat_menu == 'moves':
            for i, move in enumerate(moves):
                col = i % 2
                row = i // 2
                move_surf = small_font.render(f"{i+1}. {move[0]}", True, (200, 200, 200))
                _screen.blit(move_surf, (30 + col * 230, 350 + row * 34))
            back = tiny_font.render("B — back", True, (100, 100, 100))
            _screen.blit(back, (30, 460))

        elif _combat_menu == 'info':
            # Header — each label drawn at its fixed column x
            _screen.blit(tiny_font.render("Move", True, (140, 140, 140)), (COL_NAME, 345))
            _screen.blit(tiny_font.render("Pwr",  True, (140, 140, 140)), (COL_PWR,  345))
            _screen.blit(tiny_font.render("Uses", True, (140, 140, 140)), (COL_USES, 345))
            _screen.blit(tiny_font.render("Type", True, (140, 140, 140)), (COL_TYPE, 345))
            pygame.draw.line(_screen, (60, 60, 60), (30, 362), (460, 362), 1)

            for i, move in enumerate(moves):
                # move format: [name, power, accuracy, uses_max, uses_temp, duration, type]
                row_y = 368 + i * 26
                _screen.blit(tiny_font.render(f"{i+1}. {move[0]}", True, (200, 200, 200)), (COL_NAME, row_y))
                _screen.blit(tiny_font.render(str(move[1]), True, (200, 200, 200)),         (COL_PWR,  row_y))
                _screen.blit(tiny_font.render(str(move[4]), True, (200, 200, 200)),         (COL_USES, row_y))
                _screen.blit(tiny_font.render(move[6],      True, (200, 200, 200)),         (COL_TYPE, row_y))

            back = tiny_font.render("B — back", True, (100, 100, 100))
            _screen.blit(back, (30, 460))

    elif _combat_phase == 'win':
        win_surf = combat_font.render("Victory!", True, (100, 220, 100))
        _screen.blit(win_surf, (30, 320))
        hint = small_font.render("Press ESC to return to map", True, (160, 160, 160))
        _screen.blit(hint, (30, 365))

    elif _combat_phase == 'lose':
        lose_surf = combat_font.render("Defeated...", True, (220, 80, 80))
        _screen.blit(lose_surf, (30, 320))
        hint = small_font.render("Press ESC to return to map", True, (160, 160, 160))
        _screen.blit(hint, (30, 365))

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
    _screen.fill((20,20,20))

    mini_tile = 20

    map_width_px = _MAP_WIDTH * mini_tile
    map_height_px = _MAP_HEIGHT * mini_tile

    start_x = _WIDTH//2 - map_width_px//2
    start_y = _HEIGHT//2 - map_height_px//2

    for y in range(_MAP_HEIGHT):
        for x in range(_MAP_WIDTH):

            rect = pygame.Rect(
                start_x + x*mini_tile,
                start_y + y*mini_tile,
                mini_tile,
                mini_tile
            )

            pygame.draw.rect(_screen,(60,60,60),rect)
            pygame.draw.rect(_screen,(0,0,0),rect,1)

    # Enemy tile markers on minimap
    for enemy_name, tile in _enemy_tiles.items():
        if enemy_name not in _defeated_enemies:
            bx = start_x + tile[0] * mini_tile
            by = start_y + tile[1] * mini_tile
            pygame.draw.rect(_screen, (160, 30, 30), (bx, by, mini_tile, mini_tile))

    # Player marker
    px = start_x + _player_pos[0]*mini_tile
    py = start_y + _player_pos[1]*mini_tile

    pygame.draw.rect(_screen,(220,220,220),(px,py,mini_tile,mini_tile))

    area_name = pygame.font.SysFont(None, 40).render("Area Name", True, (255, 220, 150))
    _screen.blit(area_name, (_WIDTH//2 - area_name.get_width()//2, 60))

    text = pygame.font.SysFont(None,32).render("Press ESC to close map",True,(255,255,255))
    _screen.blit(text,(_WIDTH//2-text.get_width()//2,100))


# Game loop
if __name__ == "__main__":
    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # START screen
                if _state == _START:
                    if event.key == pygame.K_RETURN:
                        _state = _CHARACTER_SELECT

                # CHARACTER SELECT controls
                elif _state == _CHARACTER_SELECT:
                    if event.key == pygame.K_a:
                        _select_index = (_select_index - 1) % len(_ROSTER)
                    if event.key == pygame.K_d:
                        _select_index = (_select_index + 1) % len(_ROSTER)
                    if event.key == pygame.K_w:
                        if _select_index >= 3:
                            _select_index -= 3
                    if event.key == pygame.K_s:
                        if _select_index < 3:
                            _select_index = min(_select_index + 3, len(_ROSTER) - 1)
                    if event.key == pygame.K_RETURN:
                        name = _ROSTER[_select_index]
                        if name in _party:
                            _party.remove(name)
                        elif len(_party) < 3:
                            _party.append(name)
                    if event.key == pygame.K_SPACE:
                        if len(_party) == 3:
                            _state = _MAP

                # MAP controls
                elif _state == _MAP:

                    if event.key == pygame.K_m:
                        _state = _MINIMAP
                    if event.key == pygame.K_b:
                        for enemy_name, tile in _enemy_tiles.items():
                            if _player_pos == tile and enemy_name not in _defeated_enemies:
                                start_combat(enemy_name)
                                _state = _BATTLE
                                break

                    if event.key == pygame.K_w:
                        _player_pos[1] -= 1

                    if event.key == pygame.K_s:
                        _player_pos[1] += 1

                    if event.key == pygame.K_a:
                        _player_pos[0] -= 1

                    if event.key == pygame.K_d:
                        _player_pos[0] += 1

                    # Keep player inside map
                    _player_pos[0] = max(0, min(_MAP_WIDTH - 1, _player_pos[0]))
                    _player_pos[1] = max(0, min(_MAP_HEIGHT - 1, _player_pos[1]))

                # BATTLE controls
                elif _state == _BATTLE:
                    if event.key == pygame.K_ESCAPE:
                        _state = _MAP

                    if _combat_phase == 'player_choose':
                        current = _combat_order[_combat_turn_idx]
                        moves = characters[current]['moves']

                        if _combat_menu == 'main':
                            if event.key == pygame.K_1:
                                _combat_menu = 'moves'
                            elif event.key == pygame.K_2:
                                _combat_menu = 'info'
                            elif event.key == pygame.K_3:
                                _state = _MAP

                        elif _combat_menu == 'moves':
                            if event.key == pygame.K_b:
                                _combat_menu = 'main'
                            else:
                                move_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                                for i, key in enumerate(move_keys):
                                    if event.key == key and i < len(moves):
                                        do_player_move(moves[i][0])
                                        break

                        elif _combat_menu == 'info':
                            if event.key == pygame.K_b:
                                _combat_menu = 'main'

                # MINIMAP controls
                elif _state == _MINIMAP:
                    if event.key == pygame.K_ESCAPE:
                        _state = _MAP

        # Draw screens
        if _state == _START:
            draw_start()

        elif _state == _CHARACTER_SELECT:
            draw_character_select()

        elif _state == _MAP:
            draw_map()

        elif _state == _BATTLE:
            draw_battle()

        elif _state == _MINIMAP:
            draw_minimap()

        pygame.display.flip()
        _clock.tick(60)
