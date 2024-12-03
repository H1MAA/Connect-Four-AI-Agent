import numpy as np
import pygame
import sys
import math

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7

SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

EMPTY = 0
AI_PIECE = 2
PLAYER_PIECE = 1

DEPTH = 2  # Depth for the Minimax algorithm

# Create the board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

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

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

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

def is_terminal_node(board):
    return np.count_nonzero(board) == ROW_COUNT * COLUMN_COUNT

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if count_connected_fours(board, AI_PIECE) > count_connected_fours(board, PLAYER_PIECE):
                return (None, 100000000000000)
            elif count_connected_fours(board, PLAYER_PIECE) > count_connected_fours(board, AI_PIECE):
                return (None, -10000000000000)
            else:  # Tie
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


# Initialize game variables
board = create_board()
game_over = False
turn = 0

pygame.init()

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")

draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 50)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION and turn == 0:  # Human player visual feedback
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:  # Human turn
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            col = int(math.floor(posx / SQUARESIZE))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)

                if np.count_nonzero(board) == ROW_COUNT * COLUMN_COUNT:
                    # Count connected fours and display results
                    player_score = count_connected_fours(board, PLAYER_PIECE)
                    ai_score = count_connected_fours(board, AI_PIECE)

                    if player_score > ai_score:
                        label = myfont.render(f"Player wins! ({player_score}-{ai_score})", 1, RED)
                    elif ai_score > player_score:
                        label = myfont.render(f"AI wins! ({ai_score}-{player_score})", 1, YELLOW)
                    else:
                        label = myfont.render("It's a tie!", 1, BLUE)

                    screen.blit(label, (40, 10))
                    game_over = True

                draw_board(board)
                turn = 1

    if turn == 1 and not game_over:  # AI turn
        col, minimax_score = minimax(board, DEPTH, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            print(board)

            if np.count_nonzero(board) == ROW_COUNT * COLUMN_COUNT:
                # Count connected fours and display results
                player_score = count_connected_fours(board, PLAYER_PIECE)
                ai_score = count_connected_fours(board, AI_PIECE)

                if player_score > ai_score:
                    label = myfont.render(f"Player wins! ({player_score}-{ai_score})", 1, RED)
                elif ai_score > player_score:
                    label = myfont.render(f"AI wins! ({ai_score}-{player_score})", 1, YELLOW)
                else:
                    label = myfont.render("It's a tie!", 1, BLUE)

                screen.blit(label, (40, 10))
                game_over = True

            draw_board(board)
            turn = 0

    if game_over:
        pygame.time.wait(5000)