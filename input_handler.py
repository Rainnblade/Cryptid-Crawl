# input_handler.py
# Handles all player keyboard input for Cryptid Crawl.
# Import this module wherever input is needed — map, combat, menus.

# --- Directional mappings for map navigation ---
# Players can type full words, single letters, or WASDt
DIRECTIONAL_NAMES = {
    'w': 'north', 'north': 'north', 'n': 'north',
    's': 'south', 'south': 'south',
    'a': 'west',  'west': 'west',  'l': 'west',
    'd': 'east',  'east': 'east',  'r': 'east',
}

VALID_DIRECTIONS = {'north', 'south', 'east', 'west'}


def get_direction():
    """Ask the player which direction to move. Returns 'north', 'south', 'east', 'west', 'map', or 'quit'."""
    while True:
        raw = input("Move [W/A/S/D or North/South/East/West] (or 'map' to view, 'quit' to exit): ").strip().lower()

        if raw in ('quit', 'exit'):
            return 'quit'
        if raw == 'map':
            return 'map'

        direction = DIRECTIONAL_NAMES.get(raw)
        if direction:
            return direction

        print(f"  Invalid input '{raw}'. Use W/A/S/D or North/South/East/West.")


def get_combat_action(moves):
    """
    Show the combat menu and return what the player chose.

    Args:
        moves: list of moves for the player's character.
               Each move is expected as [name, ...] (e.g. ['axe swing', 70, 80, 10, 10, 0, 'physical'])

    Returns a dictionary with the player's choice:
        {'action': 'attack', 'move_index': int}  -- player chose a move (index matches position in moves list)
        {'action': 'item'}                        -- player chose to use an item
        {'action': 'flee'}                        -- player chose to flee
    """
    print("\n--- Combat Actions ---")

    # Print numbered move options
    for i, move in enumerate(moves, start=1):
        move_name = move[0] if isinstance(move, (list, tuple)) else move
        print(f"  {i}. {move_name}")

    # Fixed options after moves
    item_option = len(moves) + 1
    flee_option = len(moves) + 2
    print(f"  {item_option}. Use Item")
    print(f"  {flee_option}. Flee")
    print("----------------------")

    while True:
        raw = input("Choose an action: ").strip()

        if not raw.isdigit():
            print("  Enter a number from the list.")
            continue

        choice = int(raw)

        if 1 <= choice <= len(moves):
            return {'action': 'attack', 'move_index': choice - 1}
        elif choice == item_option:
            return {'action': 'item'}
        elif choice == flee_option:
            return {'action': 'flee'}
        else:
            print(f"  Please enter a number between 1 and {flee_option}.")


def get_menu_choice(prompt, options):
    """
    Generic numbered menu — use this for character selection, main menu, item selection, etc.

    Args:
        prompt:  string to display above the menu (e.g. "Select a character:")
        options: list of strings to display as numbered choices

    Returns the 0-based index of the chosen option.

    Example:
        idx = get_menu_choice("Pick a character:", ["Bigfoot", "Mothman", "Jersey Devil"])
        chosen = characters[idx]
    """
    print(f"\n{prompt}")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")

    while True:
        raw = input("Enter choice: ").strip()

        if not raw.isdigit():
            print("  Enter a number from the list.")
            continue

        choice = int(raw)
        if 1 <= choice <= len(options):
            return choice - 1

        print(f"  Please enter a number between 1 and {len(options)}.")


def get_confirmation(prompt):
    """
    Ask the player a yes/no question.

    Args:
        prompt: the question to display (e.g. "Are you sure you want to flee?")

    Returns True for yes, False for no.
    """
    while True:
        raw = input(f"{prompt} [y/n]: ").strip().lower()
        if raw in ('y', 'yes'):
            return True
        if raw in ('n', 'no'):
            return False
        print("  Please enter 'y' or 'n'.")
