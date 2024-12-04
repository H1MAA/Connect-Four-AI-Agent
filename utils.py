import numpy as np
import math

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

class Node:
    def __init__(self, board_str, move=None, score=None, parent=None, player=None):
        self.board_str = board_str    # Board state as a string
        self.move = move              # The move (column index) that led to this node
        self.score = score            # Heuristic score of the node
        self.parent = parent          # Parent node
        self.children = []            # List of child nodes
        self.player = player          # Which player's move it is

# Conversion Functions
def string_to_array(board_str):
    """Convert a string board state to a numpy array."""
    return np.array([int(cell) for cell in board_str]).reshape(ROW_COUNT, COLUMN_COUNT)

def array_to_string(board_array):
    """Convert a numpy array board state to a string."""
    return ''.join(map(str, board_array.flatten().astype(int)))

# Core Functions
def is_valid_location(board_array, col):
    """Check if a move in the column is valid in array state."""
    return board_array[ROW_COUNT - 1][col] == EMPTY

def get_valid_moves(board_array):
    """Get a list of valid columns for a move in array state."""
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board_array, col)]

def get_next_open_row(board_array, col):
    """Get the next available row in a column for an array-based state."""
    for r in range(ROW_COUNT):
        if board_array[r][col] == EMPTY:
            return r
    return -1  # No valid row found

def drop_piece(board_array, row, col, player):
    """Drop a piece in the given column for an array-based state."""
    board_array[row][col] = int(player)

def is_terminal_node(board_array):
    """Check if the game has reached a terminal state."""
    return np.count_nonzero(board_array) == ROW_COUNT * COLUMN_COUNT

def traverse_tree(node, prefix=""):
    print(f"{prefix}Player: {node.player}, Move: {node.move}, Score: {node.score}")
    children = node.children
    for i, child in enumerate(children):
        if i == len(children) - 1:
            new_prefix = prefix + "    "
            branch = "└── "
        else:
            new_prefix = prefix + "│   "
            branch = "├── "
        traverse_tree(child, new_prefix + branch)

def count_connected_fours(board, piece):
    count = 0
    # Check horizontal
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                count += 1
    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                count += 1
    # Check positive diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                count += 1
    # Check negative diagonals
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                count += 1
    return count

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # Horizontal scoring
    for r in range(ROW_COUNT):
        row_array = list(board[r, :])
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Vertical scoring
    for c in range(COLUMN_COUNT):
        col_array = list(board[:, c])
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Positive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative sloped diagonal
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

def minimax(board_str, depth, maximizingPlayer, parent_node=None):
    board_array = string_to_array(board_str)  # Convert to array at the start
    valid_moves = get_valid_moves(board_array)
    is_terminal = is_terminal_node(board_array)

    player = AI_PIECE if maximizingPlayer else PLAYER_PIECE
    current_node = Node(board_str=board_str, parent=parent_node, player=player)

    if depth == 0 or is_terminal:
        score = score_position(board_array, AI_PIECE)
        current_node.score = score
        return None, score, current_node
            
    if maximizingPlayer:
        value = -math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            
            _, new_score, child_node = minimax(array_to_string(temp_board), depth - 1, False, current_node)
            child_node.move = col
            current_node.children.append(child_node)
            
            if new_score is not None and new_score > value:
                value = new_score
                best_col = col
        current_node.score = value
        return best_col, value, current_node
    else:
        value = math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)

            _, new_score, child_node = minimax(array_to_string(temp_board), depth - 1, True, current_node)
            child_node.move = col
            current_node.children.append(child_node)            
            
            if new_score is not None and new_score < value:
                value = new_score
                best_col = col
        
        current_node.score = value
        return best_col, value, current_node

# Updated Minimax
def minimax_alpha_beta(board_str, depth, alpha, beta, maximizingPlayer):
    """
    Minimax algorithm using string representation for input.
    Converts to array for operations and uses array state throughout recursion.
    """
    board_array = string_to_array(board_str)  # Convert to array at the start
    valid_moves = get_valid_moves(board_array)
    is_terminal = is_terminal_node(board_array)

    if depth == 0 or is_terminal:
        if is_terminal:
            # Count connected fours to determine the outcome
            if count_connected_fours(board_array, AI_PIECE) > count_connected_fours(board_array, PLAYER_PIECE):
                return (None, 100000000000000)
            elif count_connected_fours(board_array, PLAYER_PIECE) > count_connected_fours(board_array, AI_PIECE):
                return (None, -10000000000000)
            else:  # Tie
                return (None, 0)
        else:
            return (None, score_position(board_array, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = minimax_alpha_beta(array_to_string(temp_board), depth - 1, alpha, beta, False)[1]
            if new_score is not None and new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:  # Minimizing player
        value = math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax_alpha_beta(array_to_string(temp_board), depth - 1, alpha, beta, True)[1]
            if new_score is not None and new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def expecti_minimax(board_str, depth, alpha, beta, maximizingPlayer):
    board_array = string_to_array(board_str)  # Convert to array at the start
    valid_moves = get_valid_moves(board_array)
    is_terminal = is_terminal_node(board_array)

    if depth == 0 or is_terminal:
        if is_terminal:
            if count_connected_fours(board_array, AI_PIECE) > count_connected_fours(board_array, PLAYER_PIECE):
                return (None, 100000000000000)
            elif count_connected_fours(board_array, PLAYER_PIECE) > count_connected_fours(board_array, AI_PIECE):
                return (None, -10000000000000)
            else:  # Tie
                return (None, 0)
        else:
            return (None, score_position(board_array, AI_PIECE))
    
    if maximizingPlayer:
        value = -math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = expecti_minimax(array_to_string(temp_board), depth - 1, alpha, beta, False)[1]
            # Calculate weighted average score
            weighted_score = 0.6 * new_score
            if col > 0 and is_valid_location(board_array, col - 1):
                row_left = get_next_open_row(board_array, col - 1)
                temp_board_left = board_array.copy()
                drop_piece(temp_board_left, row_left, col - 1, AI_PIECE)
                new_score_left = expecti_minimax(array_to_string(temp_board_left), depth - 1, alpha, beta, False)[1]
                weighted_score += 0.2 * new_score_left
            if col < COLUMN_COUNT - 1 and is_valid_location(board_array, col + 1):
                row_right = get_next_open_row(board_array, col + 1)
                temp_board_right = board_array.copy()
                drop_piece(temp_board_right, row_right, col + 1, AI_PIECE)
                new_score_right = expecti_minimax(array_to_string(temp_board_right), depth - 1, alpha, beta, False)[1]
                weighted_score += 0.2 * new_score_right

            if weighted_score > value:
                value = weighted_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = None
        for col in valid_moves:
            row = get_next_open_row(board_array, col)
            temp_board = board_array.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = expecti_minimax(array_to_string(temp_board), depth - 1, alpha, beta, True)[1]
            weighted_score = 0.6 * new_score
            if col > 0 and is_valid_location(board_array, col - 1):
                row_left = get_next_open_row(board_array, col - 1)
                temp_board_left = board_array.copy()
                drop_piece(temp_board_left, row_left, col - 1, PLAYER_PIECE)
                new_score_left = expecti_minimax(array_to_string(temp_board_left), depth - 1, alpha, beta, True)[1]
                weighted_score += 0.2 * new_score_left
            if col < COLUMN_COUNT - 1 and is_valid_location(board_array, col + 1):
                row_right = get_next_open_row(board_array, col + 1)
                temp_board_right = board_array.copy()
                drop_piece(temp_board_right, row_right, col + 1, PLAYER_PIECE)
                new_score_right = expecti_minimax(array_to_string(temp_board_right), depth - 1, alpha, beta, True)[1]
                weighted_score += 0.2 * new_score_right

            if weighted_score < value:
                value = weighted_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value
