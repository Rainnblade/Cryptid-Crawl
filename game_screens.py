"""

This script creates a basic RPG framework with four game states:
- START: Displays a start screen
- CHARACTER_SELECT: Grid-based party selection screen (choose 3 of 5 cryptids)
- MAP: Shows a grid-based map where the player can move
- MINIMAP: Displays a mini map when M is pressed
- BATTLE: Displays a placeholder battle screen

Controls:
- ENTER: Start the game / select or deselect a character
- SPACE: Confirm party selection (when 3 are chosen)
- WASD: Navigate character select grid / move player on the map
- M: Open minimap
- B: Enter battle screen
- ESC: Return to map (from battle or minimap)
"""

import pygame
import sys
from characters import characters

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cryptid Crawl")

clock = pygame.time.Clock()

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

        # Placeholder box — replace the next two lines with screen.blit(sprites[name], (x, y)) when sprites are ready
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
    Each tile is outlined for visibility. Also renders the player as
    a blue square at the current player_pos.
    """

    screen.fill((30, 30, 30))

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):

            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(screen, (80, 80, 80), rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

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

    Displays a placeholder battle screen with a prompt to return to the map.
    Press ESC to exit back to the map.
    """
    screen.fill((20, 20, 20))
    text = font.render("BATTLE!", True, (255,255,255))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
    
    text2 = pygame.font.SysFont(None, 32).render("Press ESC to return", True, (255,255,255))
    screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 300))


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
