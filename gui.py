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
        self.current_root = None  # Initialize the current root for visualization
        self.new_current_root = None  # For navigation

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
                    self.update_sidebar = True  # Update sidebar
                elif depth_down_button.collidepoint(pos) and self.depth > 1:
                    self.depth -= 1
                    self.update_sidebar = True  # Update sidebar
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
                    self.update_sidebar = True  # Update sidebar
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
    
    def handle_node_click(self, node, pos):
        if node.rect and node.rect.collidepoint(pos):
            if node == self.current_root and node.parent:
                # Clicking on the current root node and it has a parent, so navigate back
                self.new_current_root = node.parent
            elif node != self.current_root:
                # Clicking on a child node, navigate to it
                self.new_current_root = node
            # If node == self.current_root and no parent, do nothing (we're at the top)
            return True
        # No need to check child nodes since we're handling all nodes here
        # Alternatively, if you have a list of nodes or want to check child nodes:
        for child in node.children:
            if self.handle_node_click(child, pos):
                return True
        return False

    def draw_tree(self, screen, node, x, y):
        node_radius = 30  # Larger node radius for better visibility
        node_color = RED if node.player == PLAYER_PIECE else YELLOW
        pygame.draw.circle(screen, node_color, (x, y), node_radius)
        pygame.draw.circle(screen, WHITE, (x, y), node_radius, 2)

        font = pygame.font.SysFont("monospace", 20)
        # Display score
        score_text = font.render(f"Score: {node.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(x, y - node_radius - 20))
        screen.blit(score_text, score_rect)

        # Display move
        move_text = font.render(f"Move: {node.move}", True, WHITE)
        move_rect = move_text.get_rect(center=(x, y + node_radius + 20))
        screen.blit(move_text, move_rect)

        # Assign position and rect for click detection
        node.position = (x, y)
        node.rect = pygame.Rect(x - node_radius, y - node_radius, node_radius * 2, node_radius * 2)

        # Draw immediate children
        if node.children:
            num_children = len(node.children)
            spacing = 800 // (num_children + 1)  # Adjust horizontal spacing
            for i, child in enumerate(node.children):
                child_x = spacing * (i + 1)
                child_y = y + 200  # Vertical distance to child nodes

                # Draw the connection line
                pygame.draw.line(screen, WHITE, (x, y + node_radius), (child_x, child_y - 30))

                # Draw child node
                child_radius = 25
                child_color = RED if child.player == PLAYER_PIECE else YELLOW
                pygame.draw.circle(screen, child_color, (child_x, child_y), child_radius)
                pygame.draw.circle(screen, WHITE, (child_x, child_y), child_radius, 2)

                # Display child's score
                child_score_text = font.render(f"Score: {child.score}", True, WHITE)
                child_score_rect = child_score_text.get_rect(center=(child_x, child_y - child_radius - 20))
                screen.blit(child_score_text, child_score_rect)

                # Display child's move
                child_move_text = font.render(f"Move: {child.move}", True, WHITE)
                child_move_rect = child_move_text.get_rect(center=(child_x, child_y + child_radius + 20))
                screen.blit(child_move_text, child_move_rect)

                # Assign position and rect for click detection
                child.position = (child_x, child_y)
                child.rect = pygame.Rect(child_x - child_radius, child_y - child_radius, child_radius * 2, child_radius * 2)
                child.parent = node  # Ensure the parent reference is set

    def visualize_tree(self):
        saved_screen = self.screen
        visualize_screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Minimax Tree Visualization")
        running = True

        if self.minimax_tree:
            self.current_root = self.minimax_tree
            self.new_current_root = None
        else:
            # Display a message if the tree is not available
            font = pygame.font.SysFont("monospace", 30)
            text = font.render("No tree to display", True, WHITE)
            visualize_screen.fill(BLACK)
            visualize_screen.blit(text, (100, 100))
            pygame.display.update()
            pygame.time.wait(2000)
            pygame.display.set_mode(SIZE)
            pygame.display.set_caption("Connect 4")
            self.screen = saved_screen
            return

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    self.handle_node_click(self.current_root, pos)
                    if self.new_current_root:
                        self.current_root = self.new_current_root
                        self.new_current_root = None

            visualize_screen.fill(BLACK)
            if self.current_root:
                self.draw_tree(visualize_screen, self.current_root, 400, 100)
            else:
                font = pygame.font.SysFont("monospace", 30)
                text = font.render("No tree to display", True, WHITE)
                visualize_screen.blit(text, (100, 100))
            pygame.display.update()
            self.clock.tick(30)

        pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Connect 4")
        self.screen = saved_screen

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
                                self.visualize_tree()
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
                        col, _, minimax_tree_root = self.algorithm(board_str, self.depth, True)
                        self.minimax_tree = minimax_tree_root
                    else:
                        col, _, minimax_tree_root = self.algorithm(board_str, self.depth, -math.inf, math.inf, True)
                        self.minimax_tree = minimax_tree_root

                    if is_valid_location(self.board, col):
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