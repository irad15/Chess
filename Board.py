from typing import List, Tuple

import pygame

from Piece import Pawn, Rook, Knight, Bishop, Queen, King
from Square import Square


class Board:
    def __init__(self):
        ##################################
        # Fields for board construction:
        self.squares = [[Square((x, y)) for y in range(8)] for x in range(8)]
        self.white_pieces = []
        self.black_pieces = []
        self.white_king = None
        self.black_king = None
        self.white_king_rook = None
        self.black_king_rook = None
        self.white_queen_rook = None
        self.black_queen_rook = None
        self.graveyard = []
        self.current_turn = "white"  # Set initial turn to white
        self.sound = None

        ##################################
        # Fields for movement management:
        self.highlighted_square = None
        self.highlighted_square_locations = []
        self.capturable_locations = []

        ##################################
        # Fields for en-passant handling
        self.last_move = None  # Tracks the last move made: 3 value tuple : piece,start,destination
        self.en_passant_square = None
        self.en_passant_end_location = None
        self.en_passanting_pawns = []

        ##################################
        # Fields for check system
        self.check_location = None

        ##################################
        # Initialize the board (not based on the viewing angle anymore)
        self.initialize_board()

    ##################################
    """ init methods """

    def place_pawns(self, rank, color):
        """Places pawns on the given rank for the specified color."""
        for i in range(8):
            pawn = Pawn(color, self.squares[rank][i])
            self.squares[rank][i].set_piece(pawn)
            if color == "white":
                self.white_pieces.append(pawn)
            else:
                self.black_pieces.append(pawn)

    def place_back_rank_pieces(self, rank, color):
        """
        1. Creates back rank pieces (setting their color + starting_square)
        2. Adds pieces to self.squares.
        3. Adds pieces to {color}_pieces lists.
        """
        pieces = [
            Rook(color, self.squares[rank][0]),
            Knight(color, self.squares[rank][1]),
            Bishop(color, self.squares[rank][2]),
            Queen(color, self.squares[rank][3]),  # Queens always on d-file (index 3)
            King(color, self.squares[rank][4]),   # Kings always on e-file (index 4)
            Bishop(color, self.squares[rank][5]),
            Knight(color, self.squares[rank][6]),
            Rook(color, self.squares[rank][7])
        ]

        for piece in pieces:
            # Add pieces to the board
            file = piece.current_square.location[1]
            self.squares[rank][file].set_piece(piece)

            # Add pieces to the {color}_pieces list
            if color == "white":
                self.white_pieces.append(piece)
            else:
                self.black_pieces.append(piece)

    def initialize_board(self):
        """
        Initialize the board with the standard chess setup for both colors.
        No longer depends on the viewing angle.
        """
        # Standard chess setup: white pieces on ranks 6 (pawns) and 7 (back rank),
        # black pieces on ranks 1 (pawns) and 0 (back rank)
        white_back_rank, white_pawn_rank = 7, 6
        black_back_rank, black_pawn_rank = 0, 1

        # Initialize pawns + back-rank pieces for both colors
        # Adds all pieces to {color}_pieces lists
        self.place_pawns(white_pawn_rank, "white")
        self.place_pawns(black_pawn_rank, "black")
        self.place_back_rank_pieces(white_back_rank, "white")
        self.place_back_rank_pieces(black_back_rank, "black")

        # Assign kings explicitly by accessing their known positions
        kings_file = 4  # e-file (index 4)

        # 8 pawns + king's file will find the index of the kings
        self.white_king = self.white_pieces[8 + kings_file]
        self.black_king = self.black_pieces[8 + kings_file]

        # same for the 4 rooks
        king_rook_file = 7
        queen_rook_file = 0

        self.white_king_rook = self.white_pieces[8 + king_rook_file]
        self.black_king_rook = self.black_pieces[8 + king_rook_file]
        self.white_queen_rook = self.white_pieces[8 + queen_rook_file]
        self.black_queen_rook = self.black_pieces[8 + queen_rook_file]

        # remove all pieces but the king
        """for piece in self.black_pieces:
            if not isinstance(piece, King):
                self.capture_piece(piece)
        for piece in self.black_pieces:
            if not isinstance(piece, King):
                self.capture_piece(piece)
        for piece in self.black_pieces:
            if not isinstance(piece, King):
                self.capture_piece(piece)
        for piece in self.black_pieces:
            if not isinstance(piece, King):
                self.capture_piece(piece)

        for piece in self.white_pieces:
            if isinstance(piece, Pawn):
                self.capture_piece(piece)
        for piece in self.white_pieces:
            if isinstance(piece, Pawn):
                self.capture_piece(piece)
        for piece in self.white_pieces:
            if isinstance(piece, Pawn):
                self.capture_piece(piece)
        for piece in self.white_pieces:
            if isinstance(piece, Pawn):
                self.capture_piece(piece)"""

    ##################################
    """ general methods """

    def get_square(self, location: tuple[int, int]) -> Square:
        """Returns the Square object at the specified location on the board."""
        x, y = location
        return self.squares[x][y]

    def switch_turn(self):

        """
        # Switches the current turn between white and black.
        # probably the first method in the main game loop.
        """
        self.current_turn = "black" if self.current_turn == "white" else "white"
        pygame.mixer.Sound(f'sounds/{self.sound}.mp3').play()

    def highlight_moves(self, square):
        self.highlighted_square = square

        unfiltered_moves = square.piece.get_unfiltered_moves(self)
        filtered_moves = self.filter_moves(unfiltered_moves, self.highlighted_square.piece)
        self.highlighted_square_locations = filtered_moves

        # check all the moves that hold enemy team pieces
        self.capturable_locations = []
        for move in filtered_moves:
            square = self.get_square(move)
            if square.piece:
                self.capturable_locations.append(move)

    def clear_highlights(self):
        """Resets all highlighted squares and capturable locations."""
        self.highlighted_square = None
        self.highlighted_square_locations = []
        self.capturable_locations = []

    ##################################
    """ move methods """

    def capture_piece(self, piece):
        """
        Captures a piece by removing it from the board and adding it to the graveyard.
        """
        # remove Piece from Square + add to graveyard
        piece.current_square.remove_piece()
        self.graveyard.append(piece)

        if piece.color == "white":
            self.white_pieces.remove(piece)
        else:
            self.black_pieces.remove(piece)

    def move_piece(self, piece, destination_square):
        """
        Moves a piece to the specified destination square, capturing a piece if needed.
        The last_move will now store 4 values: the moved piece, the start square,
        the destination square, and the captured piece (if any).
        """
        self.sound = "move"
        start_square = piece.current_square
        captured_piece = destination_square.piece  # Check if there's a piece on the destination square

        # Remove the piece from its current square
        start_square.remove_piece()

        # Capture the piece on the destination square if present
        if captured_piece:
            self.capture_piece(captured_piece)
            self.sound = "capture"

        # Place the moving piece on the destination square
        destination_square.set_piece(piece)

        # Update the piece's current square reference
        piece.current_square = destination_square

        # Update last move - now with 4 values: moved piece, start square, destination square, and captured piece
        # used for general documentation and en-passant
        self.last_move = (piece, start_square, destination_square, captured_piece)

    def handle_en_passant(self):
        """
        Check if an EN-PASSANT move was made.
        This method now uses self.last_move to determine if an en passant capture should be performed.
        """
        piece, start_square, destination_square, captured_piece = self.last_move

        # Ensure the moved piece is a Pawn and en passant is possible
        if isinstance(piece, Pawn) and self.en_passant_end_location == destination_square.location:
            # Check if the en passanting pawn matches to the current pawn and capture the opponent's pawn
            if piece in self.en_passanting_pawns:
                # Capture the opponent's pawn via en passant
                self.capture_piece(self.en_passant_square.piece)
                self.sound = "capture"

        # Clear the en passant fields after the move
        self.en_passant_end_location = None
        self.en_passant_square = None
        self.en_passanting_pawns = []

    def handle_castling(self):
        """
        Handle castling based on the last move information.
        Uses self.last_move to check if the King performed a castling move and moves the rook accordingly.
        """
        piece, start_square, destination_square, _ = self.last_move

        # Ensure the moved piece is a King
        if isinstance(piece, King):
            row = 7 if piece.color == "white" else 0

            # Short castling (King moves to g1 for white or g8 for black)
            if destination_square.location == (row, 6) and start_square.location == (row, 4):
                rook_square = self.get_square((row, 7))  # h1 or h8
                rook_destination_square = self.get_square((row, 5))  # f1 or f8
                if rook_square.piece:
                    self.move_piece(rook_square.piece, rook_destination_square)
                    rook_destination_square.piece.has_moved = True  # Update rook's has_moved status
                    self.sound = "castle"

            # Long castling (King moves to c1 for white or c8 for black)
            elif destination_square.location == (row, 2) and start_square.location == (row, 4):
                rook_square = self.get_square((row, 0))  # a1 or a8
                rook_destination_square = self.get_square((row, 3))  # d1 or d8
                if rook_square.piece:
                    self.move_piece(rook_square.piece, rook_destination_square)
                    rook_destination_square.piece.has_moved = True  # Update rook's has_moved status
                    self.sound = "castle"

    def handle_player_pawn_promotion(self, graphics_manager):
        """
        Handle pawn promotion when a pawn reaches the last row of the board using the last move information.
        """
        piece, start_square, destination_square, captured_piece = self.last_move

        if isinstance(piece, Pawn):
            # Check if the pawn reached the last row (promotion row)
            if (piece.color == "white" and destination_square.location[0] == 0) or \
                    (piece.color == "black" and destination_square.location[0] == 7):

                # Ask the player for the promotion choice via the GraphicsManager
                promotion_choice = graphics_manager.ask_for_promotion_choice()

                # Validate promotion choice and create the appropriate piece
                if promotion_choice == "Q":
                    promoted_piece = Queen(piece.color, destination_square)
                elif promotion_choice == "R":
                    promoted_piece = Rook(piece.color, destination_square)
                elif promotion_choice == "B":
                    promoted_piece = Bishop(piece.color, destination_square)
                elif promotion_choice == "N":
                    promoted_piece = Knight(piece.color, destination_square)
                else:
                    print("Invalid choice, defaulting to Queen.")
                    promoted_piece = Queen(piece.color, destination_square)

                # Remove the pawn from the board's piece list and add the new one
                if piece.color == "white":
                    self.white_pieces.remove(piece)
                    self.white_pieces.append(promoted_piece)
                else:
                    self.black_pieces.remove(piece)
                    self.black_pieces.append(promoted_piece)

                # Replace the pawn with the promoted piece on the board
                destination_square.piece = promoted_piece

                self.sound = "promote"

    def execute_player_move(self, piece, destination_square, graphics_manager):
        self.move_piece(piece, destination_square)

        # Mark the king or rook as having moved, if applicable
        if isinstance(piece, (King, Rook)):
            piece.has_moved = True

        # Handle special moves (En Passant, Castling, Pawn Promotion)
        self.handle_en_passant()
        self.handle_castling()
        self.handle_player_pawn_promotion(graphics_manager)

    ##################################
    """ Check system """

    def get_threats_to_square(self, square: Square, color: str) -> list:
        """
        Returns all pieces of the opposite color that can move to the given square,
        effectively 'threatening' that square, excluding the opponent's king.
        """
        # Determine the opponent's pieces based on the current player's color
        opponent_pieces = self.white_pieces if color == "black" else self.black_pieces

        threats = []

        # Check each piece's possible moves to see if it threatens the given square
        for piece in opponent_pieces:
            # Skip the opponent's king - kings can not check or interfere with castling
            if isinstance(piece, King):
                continue

            possible_moves = piece.get_unfiltered_moves(self)  # Get the possible moves for the piece
            if square.location in possible_moves:  # Check if the piece can move to the square
                threats.append(piece)  # Add the piece to the list of threats

        return threats

    def filter_moves(self, unfiltered_moves: List[Tuple[int, int]], piece) -> List[Tuple[int, int]]:
        """
        Checks kings' safety by simulating moves and filtering out unsafe ones.
        """
        safe_moves = []
        original_square = piece.current_square
        pieces = self.black_pieces if piece.color == "white" else self.white_pieces
        king = self.white_king if piece.color == "white" else self.black_king

        for move in unfiltered_moves:
            """ Create an artificial setting of the board """
            target_square = self.get_square(move)
            target_piece = target_square.piece  # Save original piece at target square

            # Temporarily remove target_piece from pieces if it exists
            if target_piece:
                pieces.remove(target_piece)

            # Move the piece to the target square
            original_square.piece = None
            target_square.piece = piece
            piece.current_square = target_square

            """ Test if in this setting the king is not safe """
            check_threat_square = target_square if isinstance(piece, King) else king.current_square
            if not self.get_threats_to_square(check_threat_square, piece.color):
                safe_moves.append(move)

            """ Restore Board to original state """
            target_square.piece = target_piece  # Restore target piece
            if target_piece:
                pieces.append(target_piece)  # Re-add to pieces
            original_square.piece = piece
            piece.current_square = original_square

        return safe_moves

    def is_enemy_able_to_move(self):
        # Determine enemy pieces based on the color of the current square's piece
        enemy_pieces = self.black_pieces if self.current_turn == "white" else self.white_pieces

        able_to_move = False
        for piece in enemy_pieces:
            unfiltered_moves = piece.get_unfiltered_moves(self)
            filtered_moves = self.filter_moves(unfiltered_moves, piece)
            if filtered_moves:  # If there are any valid moves
                able_to_move = True
                break
        return able_to_move

    def check_board_state(self):
        """ checks whether the game has finished or not. """
        # Remove highlight from any king in check
        self.check_location = None

        # Check if any enemy piece can move
        enemy_able_to_move = self.is_enemy_able_to_move()

        # Determine the enemy king and check for threats to its square
        enemy_king = self.black_king if self.current_turn == "white" else self.white_king
        threats = self.get_threats_to_square(enemy_king.current_square, enemy_king.color)

        # Update check location and check for checkmate or stalemate

        if not enemy_able_to_move:
            if threats:
                self.check_location = enemy_king.current_square.location
                print("CHECKMATE!")
                self.sound = "checkmate"
            else:
                print("STALEMATE!")
                self.sound = "stalemate"

            return True

        if threats:
            self.check_location = enemy_king.current_square.location
            print("CHECK!")
            self.sound = "check"

        return False
