def string_to_array(board_str, rows, cols):
    """Convert a string representation of the board to a 2D list of integers."""
    board = []
    for r in range(rows):
        board.append([int(cell) for cell in board_str[r * cols:(r + 1) * cols]])
    return board

def array_to_string(board_array):
    """Convert a 2D array representation of the board to a string."""
    return ''.join(''.join(str(cell) for cell in row) for row in board_array)

def get_valid_moves(board_array):
    """
    Get a list of valid columns for a move.
    A column is valid if it has at least one empty cell (0).
    """
    rows = len(board_array)
    cols = len(board_array[0])
    valid_moves = []
    for col in range(cols):
        if board_array[rows - 1][col] == 0:  # Check the bottom-most cell
            valid_moves.append(col)
    return valid_moves

def drop_piece(board_array, col, player):
    """
    Drop a piece for the given player into the specified column.
    
    Args:
    - board_array: 2D list representing the board state.
    - col: The column where the piece should be dropped.
    - player: The player number (1 or 2) dropping the piece.

    Returns:
    - True if the piece was successfully dropped, False otherwise.
    """
    rows = len(board_array)
    for row in range(rows - 1, -1, -1):  # Start from the bottom row
        if board_array[row][col] == 0:
            board_array[row][col] = player
            return True
    return False  # If no empty cell found in the column

# Example usage:
rows, cols = 6, 7
initial_state = "0" * (rows * cols)  # Empty board represented as a string
board_array = string_to_array(initial_state, rows, cols)

print("Initial Board:")
for row in board_array:
    print(row)

# Test valid moves
valid_moves = get_valid_moves(board_array)
print("\nValid Moves:", valid_moves)

# Test dropping pieces
print("\nDropping pieces...")
drop_piece(board_array, 3, 1)  # Player 1 drops a piece in column 3
drop_piece(board_array, 3, 2)  # Player 2 drops a piece in column 3
drop_piece(board_array, 2, 1)  # Player 1 drops another piece in column 3
drop_piece(board_array, 2, 1)  # Player 2 drops another piece in column 3

print("\nUpdated Board:")
for row in board_array:
    print(row)

print(f"string representation of the board: {array_to_string(board_array)}")