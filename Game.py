import copy

import pygame
from pygame import MOUSEBUTTONDOWN, QUIT

from AIBot import AIBot
from Board import Board


# manages the board and graphics_manager
class Game:
    def __init__(self, graphics_manager):
        # Ask if the user wants to play with bot or in hot seat
        self.ai_enabled = graphics_manager.ask_for_mode()
        self.viewing_angle = graphics_manager.ask_for_color()
        pygame.display.set_caption("Irad's Chess Game")

        # AI player creation
        if self.ai_enabled:
            ai_bot_color = "black" if self.viewing_angle == "white" else "white"
            self.ai_bot = AIBot(self, ai_bot_color)

        # Initialize the board based on the selected viewing angle
        self.board = Board()
        pygame.mixer.Sound(f'sounds/start.mp3').play()

        self.move_log = []  # To store all board states
        self.current_log_index = -1  # Tracks current position in the move log
        self.save_board_state()

        self.graphics_manager = graphics_manager
        self.game_on = True  # for run_game
        self.finished = False  # for turn to stop when game ends

    ###########################################################
    """ Helper functions """

    def switch_viewing_angle(self):
        self.viewing_angle = "black" if self.viewing_angle == "white" else "white"
        pygame.mixer.Sound(f'sounds/switch.mp3').play()

    def save_board_state(self):
        """Store a deep copy of the current board state in the move log."""
        board_copy = copy.deepcopy(self.board)
        # If you are making a new move, remove future states (for correct redo functionality)
        self.move_log = self.move_log[:self.current_log_index + 1]
        self.move_log.append(board_copy)
        self.current_log_index += 1

    ###########################################################
    """ Input processing methods for human player in run_game() """

    def handle_square_selection(self, square_location):
        """
        Handles square selection: highlights, moves pieces, or deselects the current highlight.
        """
        # Adjust square_location if viewing from black's perspective
        if self.viewing_angle == "black":
            square_location = (7 - square_location[0], 7 - square_location[1])

        square = self.board.get_square(square_location)
        highlighted_square = self.board.highlighted_square

        # Case 1: No square is highlighted, so attempt to highlight the selected square
        if not highlighted_square:
            if square.piece and square.piece.color == self.board.current_turn:
                self.board.highlight_moves(square)

        # Case 2: A square is already highlighted
        else:
            # Case 2.1: Deselect if clicking the already highlighted square
            if square == highlighted_square:
                self.board.clear_highlights()

            # Case 2.2: Highlight a different piece of the same color
            elif square.piece and square.piece.color == highlighted_square.piece.color:
                self.board.highlight_moves(square)

            # Case 2.3: Move highlighted piece if the square is a valid move
            elif square_location in self.board.highlighted_square_locations:
                self.board.execute_player_move(highlighted_square.piece, square, self.graphics_manager)

                # Check game state and handle turn switching
                self.finished = self.board.check_board_state()
                if not self.finished:
                    self.board.switch_turn()
                else:
                    pygame.mixer.Sound(f'sounds/{self.board.sound}.mp3').play()

                # Clear highlights and save the board state
                self.board.clear_highlights()
                self.save_board_state()

            # Case 2.4: If the selected square is invalid, clear the highlights
            else:
                self.board.clear_highlights()

    def handle_keyboard_events(self, event):
        match event.key:
            case pygame.K_v:
                self.switch_viewing_angle()
            case pygame.K_r:
                self.board = Board()
                self.move_log = []  # To store all board states
                self.current_log_index = -1  # Tracks current position in the move log
                self.save_board_state()
                pygame.mixer.Sound(f'sounds/start.mp3').play()
                self.finished = False

            case pygame.K_LEFT:  # Move back in the move log
                if self.current_log_index > 0:
                    pygame.mixer.Sound(f'sounds/{self.board.sound}.mp3').play() # sound of last move

                    self.current_log_index -= 1
                    self.board = copy.deepcopy(self.move_log[self.current_log_index])

                    self.finished = False # going back disables the game ending

                    self.graphics_manager.draw_board(self.board, self.viewing_angle)

            case pygame.K_RIGHT:  # Move forward in the move log
                if self.current_log_index < len(self.move_log) - 1:
                    self.current_log_index += 1
                    self.board = copy.deepcopy(self.move_log[self.current_log_index])

                    pygame.mixer.Sound(f'sounds/{self.board.sound}.mp3').play() # sound of next move

                    self.graphics_manager.draw_board(self.board, self.viewing_angle)

                    # Check if we're back at the latest move in the move log
                    if self.current_log_index == len(self.move_log) - 1:
                        # if we are, and games has ended. make sure no input is allowed (finished becomes True)
                        self.finished = not self.board.is_enemy_able_to_move()

    def process_player_input(self):
        """
        Waits for a click or keyboard press:
        * based on a click, it calculates its location and sends it to handle_square_selection
        * for a keyboard input, sends event to handle_keyboard_events
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()

            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                square_location = (y // self.graphics_manager.square_size, x // self.graphics_manager.square_size)

                # Allow square selection only if it's the human's turn or AI is disabled
                if not (self.ai_enabled and self.board.current_turn == self.ai_bot.color) and not self.finished:
                    self.handle_square_selection(square_location)

            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard_events(event)

    ###########################################################
    """ run_game loop: (draw => process human/bot => draw => process human/bot ...) """

    def run_game(self):
        while self.game_on:
            # 1. Draw the current state of the board + highlights.
            self.graphics_manager.draw_board(self.board, self.viewing_angle)

            # 2. Check if we are at the present move (latest move in the log)
            at_latest_move = self.current_log_index == len(self.move_log) - 1

            # 3. If it's the AI's turn, and we are at the present, let AI make a move
            if (self.ai_enabled
                    and self.board.current_turn == self.ai_bot.color
                    and at_latest_move
                    and not self.finished):
                self.ai_bot.handle_ai_turn()

            # 4. If it's the human player's turn, or we are reviewing previous moves, handle player input
            else:
                self.process_player_input()
