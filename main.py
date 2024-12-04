from utils import *
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

DEPTH = 1  # Depth for the Minimax algorithm

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

# Create the board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

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
        board_str = array_to_string(board)  # Convert board to string
        print(f"Board string: {board_str}")  # Debugging print statement
        col, _, minimax_tree_root = minimax(board_str, DEPTH, True)
        traverse_tree(minimax_tree_root)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

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