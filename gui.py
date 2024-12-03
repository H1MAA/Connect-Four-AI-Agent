import pygame
import sys
import numpy as np
import math
from utils import *

# Constants
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
COLUMN_COUNT = 7
ROW_COUNT = 6
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
SIDE_PANEL_WIDTH = 250  # Width for the side panel to display scores and button
TOTAL_WIDTH = WIDTH + SIDE_PANEL_WIDTH
SIZE = (TOTAL_WIDTH, HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (169, 169, 169)

PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

class ConnectFourGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Connect 4")
        self.font = pygame.font.SysFont("monospace", 50)
        self.small_font = pygame.font.SysFont("monospace", 30)
        self.smaller_font = pygame.font.SysFont("monospace", 18)
        self.clock = pygame.time.Clock()

        self.depth = 4
        self.algorithm = minimax_alpha_beta
        self.algorithm_name = "Minimax Alpha-Beta"
        self.game_over = False
        self.turn = 0

        self.player_score = 0
        self.ai_score = 0

        self.state = "menu"  # Can be "menu", "settings", or "game"

        # Add a flag to control when to update the scoreboard and button
        self.update_sidebar = True

    def draw_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Connect 4", True, BLUE)
        play_button = pygame.Rect(TOTAL_WIDTH // 2 - 100, HEIGHT // 2 - 100, 200, 50)
        settings_button = pygame.Rect(TOTAL_WIDTH // 2 - 100, HEIGHT // 2, 200, 50)

        pygame.draw.rect(self.screen, GRAY, play_button)
        pygame.draw.rect(self.screen, GRAY, settings_button)

        play_text = self.small_font.render("Play", True, BLACK)
        settings_text = self.small_font.render("Settings", True, BLACK)

        self.screen.blit(title_text, (TOTAL_WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        self.screen.blit(play_text, (
            play_button.x + (play_button.width - play_text.get_width()) // 2, play_button.y + 5))
        self.screen.blit(settings_text, (
            settings_button.x + (settings_button.width - settings_text.get_width()) // 2, settings_button.y + 5))

        pygame.display.update()
        return play_button, settings_button

    def draw_settings(self):
        self.screen.fill(BLACK)

        # Depth settings
        depth_text = self.small_font.render(f"Depth: {self.depth}", True, WHITE)
        depth_up_button = pygame.Rect(TOTAL_WIDTH // 2 + 80, HEIGHT // 4 - 15, 30, 30)
        depth_down_button = pygame.Rect(TOTAL_WIDTH // 2 - 110, HEIGHT // 4 - 15, 30, 30)

        # Algorithm settings
        algorithm_text = self.small_font.render(f"Algorithm: {self.algorithm_name}", True, WHITE)
        algo_toggle_button = pygame.Rect(TOTAL_WIDTH // 2 - 200, HEIGHT // 2 - 15, 400, 50)

        # Back button
        back_button = pygame.Rect(TOTAL_WIDTH // 2 - 50, HEIGHT - 100, 100, 50)

        # Draw depth controls
        self.screen.blit(depth_text, (
            TOTAL_WIDTH // 2 - depth_text.get_width() // 2, HEIGHT // 4 - 50))

        pygame.draw.rect(self.screen, GRAY, depth_up_button)
        pygame.draw.polygon(
            self.screen, BLACK,
            [
                (depth_up_button.x + 5, depth_up_button.y + depth_up_button.height - 5),
                (depth_up_button.x + depth_up_button.width - 5, depth_up_button.y + depth_up_button.height - 5),
                (depth_up_button.x + depth_up_button.width // 2, depth_up_button.y + 5),
            ]
        )

        pygame.draw.rect(self.screen, GRAY, depth_down_button)
        pygame.draw.polygon(
            self.screen, BLACK,
            [
                (depth_down_button.x + 5, depth_down_button.y + 5),
                (depth_down_button.x + depth_down_button.width - 5, depth_down_button.y + 5),
                (depth_down_button.x + depth_down_button.width // 2, depth_down_button.y + depth_down_button.height - 5),
            ]
        )

        # Draw algorithm toggle
        self.screen.blit(algorithm_text, (
            TOTAL_WIDTH // 2 - algorithm_text.get_width() // 2, HEIGHT // 2 - 50))
        pygame.draw.rect(self.screen, GRAY, algo_toggle_button)
        algo_toggle_text = self.small_font.render("Toggle Algorithm", True, BLACK)
        self.screen.blit(
            algo_toggle_text,
            (
                algo_toggle_button.x + (algo_toggle_button.width - algo_toggle_text.get_width()) // 2,
                algo_toggle_button.y + 10,
            ),
        )

        # Draw back button
        pygame.draw.rect(self.screen, GRAY, back_button)
        back_text = self.small_font.render("Back", True, BLACK)
        self.screen.blit(
            back_text,
            (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + 10),
        )

        pygame.display.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if depth_up_button.collidepoint(pos):
                    self.depth += 1
                elif depth_down_button.collidepoint(pos) and self.depth > 1:
                    self.depth -= 1
                elif algo_toggle_button.collidepoint(pos):
                    # Toggle algorithm and update the function reference and name
                    if self.algorithm_name == "Minimax Alpha-Beta":
                        self.algorithm_name = "Expectiminimax"
                        self.algorithm = expecti_minimax  # Assign function reference
                    elif self.algorithm_name == "Expectiminimax":
                        self.algorithm_name = "Minimax"
                        self.algorithm = minimax  # Assign function reference
                    else:
                        self.algorithm_name = "Minimax Alpha-Beta"
                        self.algorithm = minimax_alpha_beta  # Assign function reference
                elif back_button.collidepoint(pos):
                    self.state = "menu"

    def draw_board(self, board):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(self.screen, BLUE, (
                    c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(self.screen, BLACK, (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                if board[r][c] == PLAYER_PIECE:
                    pygame.draw.circle(self.screen, RED, (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
                elif board[r][c] == AI_PIECE:
                    pygame.draw.circle(self.screen, YELLOW, (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

    def draw_sidebar(self):
        # Draw the sidebar background
        pygame.draw.rect(self.screen, DARK_GRAY, (WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT))

        # Draw the scores
        player_score_text = self.small_font.render(f"Player: {self.player_score}", True, RED)
        ai_score_text = self.small_font.render(f"AI: {self.ai_score}", True, YELLOW)
        self.screen.blit(player_score_text, (WIDTH + 10, 20))
        self.screen.blit(ai_score_text, (WIDTH + 10, 60))

        # Draw the current algorithm
        algorithm_label = self.small_font.render("Algorithm:", True, WHITE)
        algorithm_name_text = self.smaller_font.render(self.algorithm_name, True, WHITE)  # Use smaller font
        self.screen.blit(algorithm_label, (WIDTH + 10, 110))
        self.screen.blit(algorithm_name_text, (WIDTH + 10, 140))

        # Draw the current depth
        depth_text = self.small_font.render(f"Depth: {self.depth}", True, WHITE)
        self.screen.blit(depth_text, (WIDTH + 10, 180))

        # Draw the "Visualize Tree" button
        visualize_button = pygame.Rect(WIDTH + 10, HEIGHT - 190, 180, 80)
        pygame.draw.rect(self.screen, GRAY, visualize_button)
        
        # Split the text into two lines
        visualize_text_line1 = self.small_font.render("Visualize", True, BLACK)
        visualize_text_line2 = self.small_font.render("Tree", True, BLACK)
        self.screen.blit(
            visualize_text_line1,
            (
                visualize_button.x + (visualize_button.width - visualize_text_line1.get_width()) // 2,
                visualize_button.y + 10,
            ),
        )
        self.screen.blit(
            visualize_text_line2,
            (
                visualize_button.x + (visualize_button.width - visualize_text_line2.get_width()) // 2,
                visualize_button.y + 40,
            ),
        )

        # Draw the "Back" button
        back_button = pygame.Rect(WIDTH + 10, HEIGHT - 90, 180, 40)
        pygame.draw.rect(self.screen, GRAY, back_button)
        back_text = self.small_font.render("Back", True, BLACK)
        self.screen.blit(
            back_text,
            (
                back_button.x + (back_button.width - back_text.get_width()) // 2,
                back_button.y + 5,
            ),
        )
        pygame.display.update()

    def main_loop(self):
        while True:
            if self.state == "menu":
                play_button, settings_button = self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if play_button.collidepoint(pos):
                            self.state = "game"
                            self.game_over = False
                            self.board = np.zeros((ROW_COUNT, COLUMN_COUNT))
                            self.turn = 0
                            # Reset scores
                            self.player_score = 0
                            self.ai_score = 0
                            self.update_sidebar = True  # Update sidebar on game start
                        elif settings_button.collidepoint(pos):
                            self.state = "settings"

            elif self.state == "settings":
                self.draw_settings()

            elif self.state == "game":
                self.draw_board(self.board)
                if self.update_sidebar:
                    self.draw_sidebar()
                    self.update_sidebar = False  # Reset flag after updating

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEMOTION and self.turn == 0:
                        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        posx = event.pos[0]
                        if posx < WIDTH:
                            pygame.draw.circle(self.screen, RED, (
                                posx, int(SQUARESIZE / 2)), RADIUS)
                        pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if pos[0] > WIDTH:
                            # Check if the "Visualize Tree" button is clicked
                            visualize_button = pygame.Rect(WIDTH + 10, HEIGHT - 190, 180, 80)
                            back_button = pygame.Rect(WIDTH + 10, HEIGHT - 90, 180, 40)
                            if visualize_button.collidepoint(pos):
                                # Future implementation for visualization
                                pass
                            elif back_button.collidepoint(pos):
                                self.state = "menu"
                        elif self.turn == 0 and pos[0] < WIDTH:
                            pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                            posx = pos[0]
                            col = int(math.floor(posx / SQUARESIZE))

                            if is_valid_location(self.board, col):
                                row = get_next_open_row(self.board, col)
                                drop_piece(self.board, row, col, PLAYER_PIECE)

                                # Update player score after move
                                self.player_score = count_connected_fours(self.board, PLAYER_PIECE)
                                self.update_sidebar = True  # Update sidebar after move

                                self.turn = 1
                                self.draw_board(self.board)

                if self.turn == 1 and not self.game_over:
                    # AI's Turn
                    board_str = array_to_string(self.board)
                    if self.algorithm_name == "Minimax":
                        col, _ = self.algorithm(board_str, self.depth, True)
                    else:
                        col, _ = self.algorithm(board_str, self.depth, -math.inf, math.inf, True)

                    if is_valid_location(self.board, col):
                        pygame.time.wait(500)  # Add delay for AI move
                        row = get_next_open_row(self.board, col)
                        drop_piece(self.board, row, col, AI_PIECE)

                        # Update AI score after move
                        self.ai_score = count_connected_fours(self.board, AI_PIECE)
                        self.update_sidebar = True  # Update sidebar after move

                        self.turn = 0
                        self.draw_board(self.board)

                # **Only set game over when the board is full**
                if np.count_nonzero(self.board) == ROW_COUNT * COLUMN_COUNT:
                    # Determine the winner based on scores
                    if self.player_score > self.ai_score:
                        label = self.font.render(f"Player wins! ({self.player_score}-{self.ai_score})", True, RED)
                    elif self.ai_score > self.player_score:
                        label = self.font.render(f"AI wins! ({self.ai_score}-{self.player_score})", True, YELLOW)
                    else:
                        label = self.font.render("It's a tie!", True, BLUE)

                    self.screen.blit(label, (40, 10))
                    pygame.display.update()
                    pygame.time.wait(5000)
                    self.state = "menu"
                    continue  # Restart loop to go back to menu

            self.clock.tick(60)

if __name__ == "__main__":
    game = ConnectFourGUI()
    game.main_loop()