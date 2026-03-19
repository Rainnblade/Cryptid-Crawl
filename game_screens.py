"""

This script creates a basic RPG framework with three game states:
- START: Displays a start screen
- MAP: Shows a grid-based map where the player can move
- MINIMAP: Displays a mini map when m is pressed

Controls:
- ENTER: Start the game
- Arrow Keys: Move player on the map
- ESC: Return to map (from battle)
"""

import pygame
import sys

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cryptid Crawl")

clock = pygame.time.Clock()

# Game states
START = "start"
MAP = "map"
MINIMAP = "minimap"

state = START

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
    a centered message prompting the user to press ENTER        to begin the game.
    """

    screen.fill((30, 30, 30))

    title = font.render("Press ENTER to Start", True, (255,255,255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2))


# Draw Main Map
def draw_map():
    """
    Render the map screen.
    Draws a grid-based map using TILE_SIZE, MAP_WIDTH, and MAP_HEIGHT.
    Each tile is outlined for visibility. Also renders the player as
    a blue square at the current player_pos.
    """

    screen.fill((0,100,0))

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):

            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(screen, (0,150,0), rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Draw player
    px = player_pos[0]*TILE_SIZE
    py = player_pos[1]*TILE_SIZE

    pygame.draw.rect(screen, (0,0,255), (px,py,TILE_SIZE,TILE_SIZE))



# Draw Mini Map
def draw_minimap():

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

            pygame.draw.rect(screen,(80,80,80),rect)
            pygame.draw.rect(screen,(0,0,0),rect,1)

    # Player marker
    px = start_x + player_pos[0]*mini_tile
    py = start_y + player_pos[1]*mini_tile

    pygame.draw.rect(screen,(0,0,255),(px,py,mini_tile,mini_tile))

    text = pygame.font.SysFont(None,32).render("Press ESC to close map",True,(255,255,255))
    screen.blit(text,(WIDTH//2-text.get_width()//2,100))


# Game loop
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
                    state = MAP

            # MAP controls
            elif state == MAP:

                if event.key == pygame.K_m:
                    state = MINIMAP

                if event.key == pygame.K_UP:
                    player_pos[1] -= 1

                if event.key == pygame.K_DOWN:
                    player_pos[1] += 1

                if event.key == pygame.K_LEFT:
                    player_pos[0] -= 1

                if event.key == pygame.K_RIGHT:
                    player_pos[0] += 1

                # Keep player inside map
                player_pos[0] = max(0, min(MAP_WIDTH-1, player_pos[0]))
                player_pos[1] = max(0, min(MAP_HEIGHT-1, player_pos[1]))


            # MINIMAP controls
            elif state == MINIMAP:
                if event.key == pygame.K_ESCAPE:
                    state = MAP


    # Draw screens
    if state == START:
        draw_start()

    elif state == MAP:
        draw_map()

    elif state == MINIMAP:
        draw_minimap()

    pygame.display.flip()
    clock.tick(60)