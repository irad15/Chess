from abc import ABC, abstractmethod

from typing import List, Tuple


class Piece(ABC):
    def __init__(self, color: str, starting_square):
        self.color = color  # "white" or "black"
        self.current_square = starting_square  # Reference to the square this piece is currently on
        self.image_path = None  # Path to the image representing the piece

    @abstractmethod
    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        """
        Returns a list of normal tuples. each tuple describes a destination square.
        Returns all moves possible by a piece without:
        1. without subtracting moves due to checks and pins
        """
        pass

    # used for Queen, Rook and Bishop to find unfiltered_moves
    def traverse_in_direction(self, board, start_row: int, start_col: int,
                              vertical_direction: int, horizontal_direction: int) -> List[Tuple[int, int]]:
        """
        Helper method to traverse the board in a specific direction
        until the edge of the board or a blocking piece is encountered.
        """
        moves = []
        current_row, current_col = start_row, start_col

        # in each iteration we advance further in direction
        while True:
            current_row += vertical_direction
            current_col += horizontal_direction

            # Check if the position is out of bounds
            if not (0 <= current_row < 8 and 0 <= current_col < 8):
                break

            square = board.get_square((current_row, current_col))

            if square.is_occupied():
                if square.piece.color != self.color:  # Can capture opponent's piece
                    moves.append((current_row, current_col))
                break  # Stop advancing in this direction, as the piece blocks further movement
            else:
                moves.append((current_row, current_col))

        return moves


class Pawn(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_pawn.png"

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Determine the direction the pawn moves based on its color
        forward = -1 if self.color == "white" else 1

        # 1. Forward movement: one square forward
        forward_square = board.get_square((current_row + forward, current_col))
        if not forward_square.is_occupied():
            possible_moves.append((current_row + forward, current_col))

            # 2. Two squares forward only from the starting rank
            if (self.color == "white" and current_row == 6) or (self.color == "black" and current_row == 1):
                two_squares_forward = board.get_square((current_row + 2 * forward, current_col))
                if not two_squares_forward.is_occupied():
                    possible_moves.append((current_row + 2 * forward, current_col))

        # 3. Capturing diagonally
        for dy in [-1, 1]:  # Check both diagonals
            if 0 <= current_col + dy <= 7:  # Ensure we're within board bounds
                diagonal_square = board.get_square((current_row + forward, current_col + dy))
                if diagonal_square.is_occupied() and diagonal_square.piece.color != self.color:
                    possible_moves.append((current_row + forward, current_col + dy))

        # 4. En passant capture - conditions
        # If there was a previous move (board.last_move is not None; only false on the first turn)
        if board.last_move:
            last_piece, start_square, end_square, captured_piece = board.last_move

            # Check if the last move was a pawn moving two squares forward
            if isinstance(last_piece, Pawn) and abs(start_square.location[0] - end_square.location[0]) == 2:

                # Check if the opponent's pawn is in the same row as our pawn and is
                # adjacent to our column (+-1 column difference)
                if end_square.location[0] == current_row and abs(end_square.location[1] - current_col) == 1:

                    # All en passant conditions are met, so we record information
                    # to validate the capture later in `handle_square_selection`.
                    # These three fields will allow `handle_square_selection` to
                    # verify if the move is a valid en passant capture:

                    # 1. `board.en_passant_end_location`: The location where our
                    #     pawn will land after performing the en passant.
                    #     This will help confirm the destination square during move selection.
                    board.en_passant_end_location = (current_row + forward, end_square.location[1])

                    # 2. `board.en_passant_square`: The square containing the opponent's
                    #     pawn that is vulnerable to en passant capture.
                    #     This square is where the pawn being captured is located.
                    board.en_passant_square = board.get_square((current_row, end_square.location[1]))

                    # 3. `board.en_passanting_pawns`: This field keeps
                    #     track of the specific pawn eligible to perform en passant.
                    #     This ensures that only this pawn can attempt the capture and not other pieces.
                    board.en_passanting_pawns.append(self)

                    # Add the potential en passant capture move to the possible_moves list for further evaluation.
                    possible_moves.append((current_row + forward, end_square.location[1]))

        return possible_moves


class Rook(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_rook.png"
        self.has_moved = False  # Tracks if the Rook has moved, important for castling

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Directions for rook movement: (vertical_direction, horizontal_direction)
        directions = [
            (0, 1),   # Right
            (0, -1),  # Left
            (1, 0),   # Down
            (-1, 0)   # Up
        ]

        # Iterate over all four directions
        for vertical_direction, horizontal_direction in directions:
            # Get all possible moves in the current direction
            direction_moves = self.traverse_in_direction(board, current_row, current_col,
                                                         vertical_direction, horizontal_direction)
            # Add these moves to the possible_moves list
            possible_moves.extend(direction_moves)

        return possible_moves


class Knight(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_knight.png"

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Possible L-shaped moves for a knight (row_offset, col_offset)
        knight_moves = [
            (2, 1),   # Two down, one right
            (2, -1),  # Two down, one left
            (-2, 1),  # Two up, one right
            (-2, -1), # Two up, one left
            (1, 2),   # One down, two right
            (1, -2),  # One down, two left
            (-1, 2),  # One up, two right
            (-1, -2)  # One up, two left
        ]

        # Iterate over all knight moves
        for vertical_direction, horizontal_direction in knight_moves:
            new_row = current_row + vertical_direction
            new_col = current_col + horizontal_direction

            # Check if the position is out of bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                square = board.get_square((new_row, new_col))

                # Add the move if the square is not occupied by a friendly piece
                if not square.is_occupied() or square.piece.color != self.color:
                    possible_moves.append((new_row, new_col))

        return possible_moves


class Bishop(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_bishop.png"

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Directions for bishop movement: (vertical_direction, horizontal_direction)
        directions = [
            (1, 1),   # Down-right
            (1, -1),  # Down-left
            (-1, 1),  # Up-right
            (-1, -1)  # Up-left
        ]

        # Iterate over all four diagonal directions
        for vertical_direction, horizontal_direction in directions:
            # Get all possible moves in the current diagonal direction
            direction_moves = self.traverse_in_direction(board, current_row, current_col,
                                                         vertical_direction, horizontal_direction)
            # Add these moves to the possible_moves list
            possible_moves.extend(direction_moves)

        return possible_moves


class Queen(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_queen.png"

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Directions for queen movement: both rook-like and bishop-like
        directions = [
            (0, 1),   # Right (Rook direction)
            (0, -1),  # Left (Rook direction)
            (1, 0),   # Down (Rook direction)
            (-1, 0),  # Up (Rook direction)
            (1, 1),   # Down-right (Bishop direction)
            (1, -1),  # Down-left (Bishop direction)
            (-1, 1),  # Up-right (Bishop direction)
            (-1, -1)  # Up-left (Bishop direction)
        ]

        # Iterate over all eight directions
        for vertical_direction, horizontal_direction in directions:
            # Get all possible moves in the current direction
            direction_moves = self.traverse_in_direction(board, current_row, current_col,
                                                         vertical_direction, horizontal_direction)
            # Add these moves to the possible_moves list
            possible_moves.extend(direction_moves)

        return possible_moves


class King(Piece):
    def __init__(self, color: str, current_square):
        super().__init__(color, current_square)
        self.image_path = f"images/{color}_king.png"
        self.has_moved = False  # Tracks if the King has moved, important for castling

    def get_unfiltered_moves(self, board) -> List[Tuple[int, int]]:
        possible_moves = []
        current_row, current_col = self.current_square.location

        # Directions for king movement: one square in any direction
        directions = [
            (0, 1),    # Right
            (0, -1),   # Left
            (1, 0),    # Down
            (-1, 0),   # Up
            (1, 1),    # Down-right
            (1, -1),   # Down-left
            (-1, 1),   # Up-right
            (-1, -1)   # Up-left
        ]

        # Iterate over all eight possible directions for regular moves
        for vertical_direction, horizontal_direction in directions:
            new_row = current_row + vertical_direction
            new_col = current_col + horizontal_direction

            # Check if the new position is within board bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                square = board.get_square((new_row, new_col))

                # Add the move if the square is not occupied by a friendly piece
                if not square.is_occupied() or square.piece.color != self.color:
                    possible_moves.append((new_row, new_col))

        # Check for castling moves
        # if the king hasn't moved yet: proceed
        if not self.has_moved:
            row = 7 if self.color == "white" else 0  # Determine the row for the king

            # Check if the king is currently NOT under threat
            if not board.get_threats_to_square(board.get_square((row, 4)), self.color):
                # Short castling checks
                if (not board.get_square((row, 5)).is_occupied() and  # Check square f1 or f8 (king bishop)
                        not board.get_square((row, 6)).is_occupied() and  # Check square g1 or g8 (king knight)
                        not board.get_threats_to_square(board.get_square((row, 5)), self.color) and
                        not board.get_threats_to_square(board.get_square((row, 6)), self.color)):

                    # check if the king side rook has not moved
                    rook = board.white_king_rook if self.color == "white" else board.black_king_rook
                    if not rook.has_moved:
                        possible_moves.append((row, 6))  # e1 to g1 or e8 to g8

                # Long castling checks
                if (not board.get_square((row, 3)).is_occupied() and  # Check square d1 or d8 (queen)
                        not board.get_square((row, 2)).is_occupied() and  # Check square c1 or c8 (queen bishop)
                        not board.get_square((row, 1)).is_occupied() and  # Check square b1 or b8 (queen knight)
                        not board.get_threats_to_square(board.get_square((row, 3)), self.color) and
                        not board.get_threats_to_square(board.get_square((row, 2)), self.color)):

                    # check if the queen side rook has not moved
                    rook = board.white_queen_rook if self.color == "white" else board.black_queen_rook
                    if not rook.has_moved:
                        possible_moves.append((row, 2))  # e1 to c1 or e8 to c8

        # for all these moves: check if they will put us too close to the opposite king:
        enemy_king = board.white_king if self.color == "black" else board.black_king
        enemy_king_location = enemy_king.current_square.location

        # Filter out moves that place the king too close to the opponent's king
        filtered_moves = []
        for move in possible_moves:
            # Check if the move is NOT within 1 square of the enemy king in both x and y directions
            if not (abs(move[0] - enemy_king_location[0]) <= 1 and abs(move[1] - enemy_king_location[1]) <= 1):
                filtered_moves.append(move)

        return filtered_moves
