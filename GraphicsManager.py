import pygame
from pygame import MOUSEBUTTONDOWN, QUIT


class GraphicsManager:
    def __init__(self, board_size=800):
        """Initialize the GraphicsManager with the given board size."""
        pygame.init()
        self.screen = pygame.display.set_mode((board_size, board_size))
        pygame.display.set_caption("Irad's Chess Game")
        self.board_size = board_size
        self.square_size = board_size // 8
        self.font = pygame.font.SysFont(None, 36)

    ##################################
    """ draw_board """

    def draw_squares(self, board, viewing_angle):
        """
        Draw the squares of the board, including any highlights for possible moves,
        capturable locations, check location, and add rank and file labels.
        """
        colors = [(240, 217, 181), (181, 136, 99)]  # Light and dark square colors
        highlight_color = (0, 100, 0, 120)  # Slightly darker and less transparent highlight color for possible moves
        selected_square_color = (0, 100, 0, 150)  # Darker green for the highlighted square
        capturable_color = (200, 0, 0, 120)  # Reddish color for capturable locations
        check_highlight_color = (255, 105, 180, 180)  # Pink color for check location (RGB for pink)

        # Initialize fonts for rank and file labels
        number_font = pygame.font.SysFont(None, 28)  # Numbers are slightly bigger (10% increase)
        letter_font = pygame.font.SysFont(None, 24)  # Letters remain the same size

        # Precompute file and rank labels based on viewing angle
        file_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if viewing_angle == 'white' \
            else ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        rank_labels = ['1', '2', '3', '4', '5', '6', '7', '8'] if viewing_angle == 'white' \
            else ['8', '7', '6', '5', '4', '3', '2', '1']

        # Extract last move (start and destination squares)
        last_move = board.last_move
        start_square = last_move[1] if last_move else None
        destination_square = last_move[2] if last_move else None

        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                color = colors[(row + col) % 2]  # Determine base square color

                # Adjust row/col based on the viewing angle (board inversion)
                draw_row = 7 - row if viewing_angle == 'black' else row
                draw_col = 7 - col if viewing_angle == 'black' else col

                """ Draw the base square color """
                pygame.draw.rect(self.screen, color, pygame.Rect(
                    draw_col * self.square_size, draw_row * self.square_size, self.square_size, self.square_size))

                ###############################################################
                """ Highlight last move (start and destination squares) """
                if last_move:
                    if square == start_square or square == destination_square:
                        highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                        highlight_surface.fill(highlight_color)
                        self.screen.blit(highlight_surface, (draw_col * self.square_size, draw_row * self.square_size))

                """ Draw all highlight types """
                # Highlight the selected highlighted square
                if board.highlighted_square and square == board.highlighted_square:
                    highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight_surface.fill(selected_square_color)
                    self.screen.blit(highlight_surface, (draw_col * self.square_size, draw_row * self.square_size))

                # Highlight capturable locations
                if square.location in board.capturable_locations:
                    capturable_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    capturable_surface.fill(capturable_color)
                    self.screen.blit(capturable_surface, (draw_col * self.square_size, draw_row * self.square_size))

                # Draw possible move circles, but skip capturable locations
                elif square.location in board.highlighted_square_locations:
                    highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surface, highlight_color,
                                       (self.square_size // 2, self.square_size // 2), self.square_size // 6)
                    self.screen.blit(highlight_surface, (draw_col * self.square_size, draw_row * self.square_size))

                # Highlight the check location
                if square.location == board.check_location:
                    check_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    check_surface.fill(check_highlight_color)
                    self.screen.blit(check_surface, (draw_col * self.square_size, draw_row * self.square_size))

                ###############################################################
                """ Draw rank and file labels """
                label_color = colors[(row + col + 1) % 2]  # Opposite color for the label
                if (col == 7 and viewing_angle == "white") or (col == 0 and viewing_angle == "black"):
                    rank_label = rank_labels[7 - row] if viewing_angle == 'white' else rank_labels[row]
                    rank_label_surface = number_font.render(rank_label, True, label_color)
                    self.screen.blit(rank_label_surface, (draw_col * self.square_size + self.square_size - 15,
                                                          draw_row * self.square_size + 5))

                if (row == 7 and viewing_angle == "white") or (row == 0 and viewing_angle == "black"):
                    file_label = file_labels[col] if viewing_angle == 'white' else file_labels[7 - col]
                    file_label_surface = letter_font.render(file_label, True, label_color)
                    self.screen.blit(file_label_surface, (draw_col * self.square_size + 5,
                                                          draw_row * self.square_size + self.square_size - 18))

    def draw_pieces(self, board, viewing_angle):
        """Draw all pieces on the board, adjusting for viewing angle."""
        # Depending on the viewing angle, adjust how pieces are drawn
        for row in range(8):
            for col in range(8):
                # Get the square based on viewing angle
                if viewing_angle == "white":
                    display_row = row
                    display_col = col
                else:  # "black"
                    display_row = 7 - row
                    display_col = 7 - col

                square = board.squares[row][col]
                if square.piece:
                    # Load the image of the piece
                    piece_image = pygame.image.load(square.piece.image_path)

                    # Resize the image to fit within a square on the board
                    piece_image = pygame.transform.scale(piece_image, (self.square_size, self.square_size))

                    # Blit (draw) the piece image onto the screen at the correct location
                    self.screen.blit(piece_image, (display_col * self.square_size, display_row * self.square_size))

    def draw_board(self, board, viewing_angle):
        """Draw the chessboard and pieces. updates itself after every click"""
        self.screen.fill((255, 255, 255))  # Fill the background with white
        self.draw_squares(board, viewing_angle)
        self.draw_pieces(board, viewing_angle)
        pygame.display.flip()  # updates screen

    ##################################
    """ methods for Main => Hot-seat/Bot and White/Black"""

    @staticmethod
    def create_button_rects(window_width, window_height, button_width, button_height, spacing=20):
        """Helper method to create button rectangles."""
        return [
            pygame.Rect((window_width // 2 - button_width // 2, window_height // 2 - button_height - spacing),
                        (button_width, button_height)),
            pygame.Rect((window_width // 2 - button_width // 2, window_height // 2 + spacing),
                        (button_width, button_height))
        ]

    @staticmethod
    def draw_screen_and_buttons(screen, background_color, button_rects, button_colors, texts, text_colors, font):
        """Helper method to fill the screen, draw buttons and their text."""
        screen.fill(background_color)

        # Draw buttons
        for i, button_rect in enumerate(button_rects):
            pygame.draw.rect(screen, button_colors[i], button_rect)
            text_surface = font.render(texts[i], True, text_colors[i])
            screen.blit(text_surface, (button_rect.centerx - text_surface.get_width() // 2,
                                       button_rect.centery - text_surface.get_height() // 2))

    @staticmethod
    def ask_for_mode():
        """Pygame window to ask user if they want to play with a bot or in a hot seat."""
        window_width = 800
        window_height = 800
        background_color = (60, 60, 60)
        button_width = 165
        button_height = 55

        # Colors
        button_colors = [(200, 200, 200), (100, 100, 100)]  # Bot and Hot seat button colors
        text_color = (0, 0, 0)  # Text color for both buttons
        texts = ["Play with Bot", "Hot Seat"]

        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Choose Game Mode")

        font = pygame.font.SysFont(None, 36)
        button_rects = GraphicsManager.create_button_rects(window_width, window_height, button_width, button_height)

        running = True
        while running:
            GraphicsManager.draw_screen_and_buttons(screen, background_color, button_rects,
                                                    button_colors, texts, [text_color] * 2, font)

            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rects[0].collidepoint(event.pos):
                        return True  # Return True for playing with the bot
                    elif button_rects[1].collidepoint(event.pos):
                        return False  # Return False for hot seat

            pygame.display.flip()

    @staticmethod
    def ask_for_color():
        """Pygame window to ask user if they want to play as white or black."""
        window_width = 800
        window_height = 800
        background_color = (60, 60, 60)
        button_width = 165
        button_height = 55

        # Colors
        button_colors = [(255, 255, 255), (0, 0, 0)]  # White and Black button colors
        text_colors = [(0, 0, 0), (255, 255, 255)]  # Text colors for white and black buttons
        texts = ["Play as White", "Play as Black"]

        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Choose Your Color")

        font = pygame.font.SysFont(None, 36)
        button_rects = GraphicsManager.create_button_rects(window_width, window_height, button_width, button_height)

        running = True
        while running:
            GraphicsManager.draw_screen_and_buttons(screen, background_color,
                                                    button_rects, button_colors, texts, text_colors, font)

            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rects[0].collidepoint(event.pos):
                        return "white"  # Return "white" if white button is clicked
                    elif button_rects[1].collidepoint(event.pos):
                        return "black"  # Return "black" if black button is clicked

            pygame.display.flip()

    ##################################
    """ Helper Methods  """

    def display_message(self, message):
        """Display a message on the screen."""
        text_surface = self.font.render(message, True, (255, 0, 0))
        self.screen.blit(text_surface, (self.board_size // 2 - text_surface.get_width() // 2, self.board_size - 40))

    def ask_for_promotion_choice(self):
        """Displays a set of buttons for the user to choose a promotion piece."""
        # Define button size and color
        button_width = 150
        button_height = 50
        button_color = (200, 200, 200)
        text_color = (0, 0, 0)

        # Create promotion window
        promotion_window_width = self.board_size
        promotion_window_height = 200  # Height for the promotion menu
        promotion_rect = pygame.Rect(0, (self.board_size - promotion_window_height) // 2,
                                     promotion_window_width, promotion_window_height)

        # Promotion options
        options = [("Q", "Queen"), ("R", "Rook"), ("B", "Bishop"), ("N", "Knight")]

        # Font setup
        font = pygame.font.SysFont(None, 36)

        running = True
        while running:
            self.screen.fill((255, 255, 255), promotion_rect)

            # Draw the promotion buttons
            for i, (key, name) in enumerate(options):
                button_rect = pygame.Rect(
                    (i * button_width) + (self.board_size // 2 - (2 * button_width)),
                    (self.board_size - promotion_window_height) // 2 + 50,
                    button_width,
                    button_height
                )
                pygame.draw.rect(self.screen, button_color, button_rect)

                # Draw button text
                text_surface = font.render(name, True, text_color)
                self.screen.blit(text_surface, (button_rect.centerx - text_surface.get_width() // 2,
                                                button_rect.centery - text_surface.get_height() // 2))

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                elif event.type == MOUSEBUTTONDOWN:
                    # Check which button was clicked
                    for i, (key, name) in enumerate(options):
                        button_rect = pygame.Rect(
                            (i * button_width) + (self.board_size // 2 - (2 * button_width)),
                            (self.board_size - promotion_window_height) // 2 + 50,
                            button_width,
                            button_height
                        )
                        if button_rect.collidepoint(event.pos):
                            return key  # Return the key representing the chosen promotion
