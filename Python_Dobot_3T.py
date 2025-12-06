from Python_Dobot_setup import MODE_PTP, Dobot
import time
import cv2
import numpy as np

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Board positions [x, y, z] for the 3x3 grid
BOARD_POSITIONS = {
    0: [264.24, -40.29, -43.72],   # Top-left
    1: [305.98, -42.72, -43.72],   # Top-center
    2: [343.8, -43.75, -43.72],   # Top-right
    3: [342.36, 4.21, -43.72],   # Middle-right
    4: [305.64, 3.5, -43.72],   # Center
    5: [261.72, 9.62, -43.72],   # Middle-left
    6: [265.91, 54.08, -43.72],   # Bottom-left
    7: [303.92, 50.14, -43.72],   # Bottom-center
    8: [345.84, 52.47, -43.72],    # Bottom-right
}

# Storage locations for game pieces
BLUE_STORAGE = [312.79, 128.37, -43.72]  # Base position
RED_STORAGE = [247.67, -87.59, -43.72]   # Base position

# Z-height adjustments
PIECE_HEIGHT = 10.0  # Height of each block
SAFE_HEIGHT = 50.0   # Safe travel height above board
PICKUP_OFFSET = -10.0 # How much to lower for pickup (adjust for suction)

# Game constants
EMPTY = 0
HUMAN = 1  # Human player
ROBOT = 2  # Robot player

# ============================================================================
# DOBOT INITIALIZATION
# ============================================================================

device = None

def initialize_dobot(port="COM4", home_on_init=True):
    """
    Initialize the Dobot device.

    Args:
        port: COM port for Dobot
        home_on_init: Whether to home the device on initialization

    Returns:
        Dobot device instance
    """
    global device

    if device is None:
        device = Dobot(port=port)
        if home_on_init:
            device.wait_for_cmd(device.home())
        device.speed(75, 75)
        print("Dobot initialized successfully")

    return device

# ============================================================================
# GAME STATE
# ============================================================================

class TicTacToeGame:
    def __init__(self, human_color='blue'):
        """
        Initialize the game state.

        Args:
            human_color: 'blue' or 'red' - which color the human is playing
        """
        self.board = [EMPTY] * 9  # 3x3 board represented as list
        self.human_color = human_color
        self.robot_color = 'red' if human_color == 'blue' else 'blue'
        self.pieces_remaining = {'blue': 5, 'red': 5}

    def get_cell(self, position):
        """Get the value at a board position (0-8)"""
        return self.board[position]

    def set_cell(self, position, player):
        """Set a board position to a player value"""
        self.board[position] = player

    def is_valid_move(self, position):
        """Check if a move is valid (position is empty)"""
        return 0 <= position < 9 and self.board[position] == EMPTY

    def get_available_moves(self):
        """Return list of available positions"""
        return [i for i in range(9) if self.board[i] == EMPTY]

    def check_winner(self):
        """
        Check if there's a winner.
        Returns: HUMAN, ROBOT, or None
        """
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for combo in winning_combinations:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]
                and self.board[combo[0]] != EMPTY):
                return self.board[combo[0]]

        return None

    def is_board_full(self):
        """Check if board is full (tie game)"""
        return EMPTY not in self.board

    def print_board(self):
        """Print the current board state"""
        symbols = {EMPTY: '.', HUMAN: 'H', ROBOT: 'R'}
        print("\nCurrent Board:")
        for i in range(3):
            row = [symbols[self.board[i*3 + j]] for j in range(3)]
            print(f"  {' '.join(row)}")
        print()

# ============================================================================
# AI - MINIMAX ALGORITHM
# ============================================================================

def minimax(game, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
    """
    Minimax algorithm with alpha-beta pruning for optimal move selection.

    Args:
        game: TicTacToeGame instance
        depth: Current depth in game tree
        is_maximizing: True if maximizing player (robot), False if minimizing (human)
        alpha: Alpha value for pruning
        beta: Beta value for pruning

    Returns:
        Score of the position
    """
    winner = game.check_winner()

    # Terminal states
    if winner == ROBOT:
        return 10 - depth  # Prefer faster wins
    elif winner == HUMAN:
        return depth - 10  # Prefer slower losses
    elif game.is_board_full():
        return 0  # Tie

    if is_maximizing:
        max_eval = float('-inf')
        for move in game.get_available_moves():
            game.set_cell(move, ROBOT)
            eval = minimax(game, depth + 1, False, alpha, beta)
            game.set_cell(move, EMPTY)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in game.get_available_moves():
            game.set_cell(move, HUMAN)
            eval = minimax(game, depth + 1, True, alpha, beta)
            game.set_cell(move, EMPTY)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval

def get_best_move(game):
    """
    Get the best move for the robot using minimax algorithm.

    Returns:
        Best position (0-8) to play
    """
    best_move = None
    best_value = float('-inf')

    for move in game.get_available_moves():
        game.set_cell(move, ROBOT)
        move_value = minimax(game, 0, False)
        game.set_cell(move, EMPTY)

        if move_value > best_value:
            best_value = move_value
            best_move = move

    return best_move

# ============================================================================
# PHYSICAL MOVEMENT FUNCTIONS
# ============================================================================

def move_to_safe_position(x, y):
    """Move to a safe height above a position before descending"""
    cmd_id = device.move_to(x, y, SAFE_HEIGHT, 0)
    device.wait_for_cmd(cmd_id)

def pickup_piece(color, game):
    """
    Pick up a piece from storage.

    Args:
        color: 'blue' or 'red'
        game: TicTacToeGame instance to track remaining pieces
    """
    # Determine storage location and calculate height
    storage = BLUE_STORAGE if color == 'blue' else RED_STORAGE
    pieces_used = 5 - game.pieces_remaining[color]
    z_height = storage[2] + (game.pieces_remaining[color]-1) * PIECE_HEIGHT

    print(f"Picking up {color} piece from storage...")

    # Move to safe position above storage
    move_to_safe_position(storage[0], storage[1])

    # Lower to pickup height
    cmd_id = device.move_to(storage[0], storage[1], z_height + PICKUP_OFFSET, 0)
    device.wait_for_cmd(cmd_id)
    time.sleep(0.3)

    # Activate suction
    cmd_id = device.suck(True)
    device.wait_for_cmd(cmd_id)
    time.sleep(0.5)  # Wait for suction to engage

    # Raise to safe height
    cmd_id = device.move_to(storage[0], storage[1], SAFE_HEIGHT, 0)
    device.wait_for_cmd(cmd_id)

    game.pieces_remaining[color] -= 1

def place_piece(position):
    """
    Place a piece at a board position.

    Args:
        position: Board position (0-8)
    """
    coords = BOARD_POSITIONS[position]
    x, y, z = coords

    print(f"Placing piece at position {position}...")

    # Move to safe position above target
    move_to_safe_position(x, y)

    # Lower to placement height
    cmd_id = device.move_to(x, y, z, 0)
    device.wait_for_cmd(cmd_id)
    time.sleep(0.3)

    # Release suction
    cmd_id = device.suck(False)
    device.wait_for_cmd(cmd_id)
    time.sleep(0.3)

    # Raise to safe height
    cmd_id = device.move_to(x, y, SAFE_HEIGHT, 0)
    device.wait_for_cmd(cmd_id)

def robot_make_move(position, game):
    """
    Execute a complete robot move: pickup and place.

    Args:
        position: Board position (0-8)
        game: TicTacToeGame instance
    """
    print(f"DEBUG: robot_make_move - Starting move to position {position}")
    print(f"DEBUG: robot_make_move - Robot color: {game.robot_color}")
    print(f"DEBUG: robot_make_move - Pieces remaining: {game.pieces_remaining}")

    if device is None:
        print("ERROR: Dobot device is None! Robot cannot move.")
        return

    print(f"DEBUG: robot_make_move - Calling pickup_piece({game.robot_color})")
    pickup_piece(game.robot_color, game)

    print(f"DEBUG: robot_make_move - Calling place_piece({position})")
    place_piece(position)

    print(f"DEBUG: robot_make_move - Setting cell {position} to ROBOT")
    game.set_cell(position, ROBOT)

    print(f"DEBUG: robot_make_move - Returning to home position")
    cmd_id = device.home()
    device.wait_for_cmd(cmd_id)

    print(f"DEBUG: robot_make_move - Move complete!")

# ============================================================================
# VISION SYSTEM (Camera-based move detection)
# ============================================================================

def detect_human_move(game, camera_index=1):
    """
    Detect human player's move using camera vision.
    This is a placeholder - you'll need to implement color detection
    based on your specific camera setup and lighting conditions.

    Args:
        game: TicTacToeGame instance
        camera_index: Camera device index

    Returns:
        Position (0-8) where human placed their piece, or None
    """
    # TODO: Implement actual computer vision logic
    # This should:
    # 1. Capture image from camera
    # 2. Detect the human's color blocks on the board
    # 3. Compare with previous board state
    # 4. Return the new position

    print("\n=== VISION DETECTION PLACEHOLDER ===")
    print("Implement camera-based detection here")
    print("For now, please enter the position manually (0-8):")

    while True:
        try:
            pos = int(input("Human move position: "))
            if game.is_valid_move(pos):
                game.set_cell(pos, HUMAN)
                return pos
            else:
                print("Invalid position. Try again.")
        except ValueError:
            print("Please enter a number 0-8")

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def play_game():
    """Main game loop"""
    print("=" * 50)
    print("TIC-TAC-TOE ROBOT")
    print("=" * 50)

    # Setup
    human_color = input("Choose your color (blue/red): ").lower()
    while human_color not in ['blue', 'red']:
        human_color = input("Please choose 'blue' or 'red': ").lower()

    game = TicTacToeGame(human_color=human_color)
    print(f"\nYou are playing as {human_color.upper()}")
    print(f"Robot is playing as {game.robot_color.upper()}")

    who_starts = input("\nWho starts? (human/robot): ").lower()
    while who_starts not in ['human', 'robot']:
        who_starts = input("Please choose 'human' or 'robot': ").lower()

    current_player = HUMAN if who_starts == 'human' else ROBOT

    # Game loop
    while True:
        game.print_board()

        if current_player == HUMAN:
            print("Human's turn...")
            detect_human_move(game)
            current_player = ROBOT
        else:
            print("Robot's turn...")
            best_move = get_best_move(game)
            print(f"Robot chooses position {best_move}")
            robot_make_move(best_move, game)
            current_player = HUMAN

        # Check for game end
        winner = game.check_winner()
        if winner == HUMAN:
            game.print_board()
            print("Human wins!")
            break
        elif winner == ROBOT:
            game.print_board()
            print("Robot wins!")
            break
        elif game.is_board_full():
            game.print_board()
            print("It's a tie!")
            break

    # Return home
    device.wait_for_cmd(device.home())
    print("\nGame over. Robot returned to home position.")

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_board_positions():
    """Test movement to all board positions"""
    print("Testing all board positions...")
    for pos in range(9):
        coords = BOARD_POSITIONS[pos]
        print(f"Moving to position {pos}: {coords}")
        move_to_safe_position(coords[0], coords[1])
        cmd_id = device.move_to(coords[0], coords[1], coords[2], 0)
        device.wait_for_cmd(cmd_id)
        time.sleep(1)
    device.wait_for_cmd(device.home())
    print("Position test complete")

def test_pickup_place():
    """Test pickup and place operations"""
    test_game = TicTacToeGame(human_color='blue')

    print("Testing blue piece pickup and place at position 4 (center)...")
    pickup_piece('blue', test_game)
    place_piece(4)

    print("Testing red piece pickup and place at position 0 (top-left)...")
    pickup_piece('red', test_game)
    place_piece(0)

    device.wait_for_cmd(device.home())
    print("Pickup/place test complete")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Initialize Dobot when running standalone
    initialize_dobot(port="COM4", home_on_init=True)

    print("\nWhat would you like to do?")
    print("1. Play tic-tac-toe")
    print("2. Test board positions")
    print("3. Test pickup/place")

    choice = input("\nEnter choice (1-3): ")

    if choice == "1":
        play_game()
    elif choice == "2":
        test_board_positions()
    elif choice == "3":
        test_pickup_place()
    else:
        print("Invalid choice")
