import copy
import pygame
from Piece import King, Rook, Pawn, Queen, Bishop, Knight

PIECE_VALUES = {
    Pawn: 1,
    Knight: 3,
    Bishop: 3,
    Rook: 5,
    Queen: 9,
    King: 100  # High value to prioritize king safety
}


class AIBot:
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.transposition_table = {}  # Initialize Transposition Table

    ###########################################################
    """ Helper functions """

    @staticmethod
    def evaluate_board(board):
        """
        Evaluate the board and return a score based on piece values and their positions.
        Positive scores favor AI, negative scores favor the opponent.
        """
        score = 0

        for piece in board.white_pieces:
            value = PIECE_VALUES[type(piece)]
            score += value

        for piece in board.black_pieces:
            value = PIECE_VALUES[type(piece)]
            score -= value

        return score

    @staticmethod
    def handle_ai_pawn_promotion(board):
        """
        Handle pawn promotion when a pawn reaches the last row of the board using the last move information.
        This version automatically chooses a random promotion option (Q, R, B, N).
        """
        piece, start_square, destination_square, captured_piece = board.last_move

        if isinstance(piece, Pawn):
            # Check if the pawn reached the last row (promotion row)
            if (piece.color == "white" and destination_square.location[0] == 0) or \
                    (piece.color == "black" and destination_square.location[0] == 7):

                promotion_choice = "Q"  # Always promote to a Queen for simplicity

                promoted_piece = {
                    "Q": Queen(piece.color, destination_square),
                    "R": Rook(piece.color, destination_square),
                    "B": Bishop(piece.color, destination_square),
                    "N": Knight(piece.color, destination_square)
                }[promotion_choice]

                # Remove the pawn from the board's piece list and add the new one
                if piece.color == "white":
                    board.white_pieces.remove(piece)
                    board.white_pieces.append(promoted_piece)
                else:
                    board.black_pieces.remove(piece)
                    board.black_pieces.append(promoted_piece)

                # Replace the pawn with the promoted piece on the board
                destination_square.piece = promoted_piece

                board.sound = "promote"

    """ Executes a move on any given board """
    def execute_ai_move(self, piece, location, board):
        row, col = location
        board.move_piece(piece, board.squares[row][col])

        # Mark the king or rook as having moved, if applicable
        if isinstance(piece, (King, Rook)):
            piece.has_moved = True

        # Handle special moves (En Passant, Castling, Pawn Promotion)
        board.handle_en_passant()
        board.handle_castling()
        self.handle_ai_pawn_promotion(board)

    ###########################################################
    """ minimax methods """

    @staticmethod
    def get_valid_moves(color, board):
        """Collect all valid moves for {color} pieces and a given board."""
        pieces = board.white_pieces if color == "white" else board.black_pieces
        valid_moves = []

        for piece in pieces:
            unfiltered_moves = piece.get_unfiltered_moves(board)
            filtered_moves = board.filter_moves(unfiltered_moves, piece)
            for move in filtered_moves:
                valid_moves.append((piece, move))  # Collect the piece and its valid move

        return valid_moves

    @staticmethod
    def order_moves(valid_moves, board):
        ordered_moves = []

        for piece, move in valid_moves:
            row, col = move  # Get the target row and column from the move
            destination_square = board.squares[row][col]
            move_value = 0

            # Check if the move captures an opponent's piece
            if destination_square.piece and destination_square.piece.color != piece.color:
                move_value += PIECE_VALUES[type(destination_square.piece)]  # Value of the captured piece

            # Add the move and its value to the list
            ordered_moves.append((piece, move, move_value))

        # Sort by move_value in descending order
        ordered_moves.sort(key=lambda x: x[2], reverse=True)

        return [(piece, move) for piece, move, _ in ordered_moves]

    """ Minimax + Extras """
    def minimax(self, board, depth, is_white, alpha=float('-inf'), beta=float('inf')):
        # Hash the current board state
        """ Hash function to represent the board state """
        board_hash = hash(str(board.squares))

        # Check if this board state has already been evaluated
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash], None

        # Base case: if depth is zero or the game is over
        if depth == 0 or board.check_board_state():
            evaluation = self.evaluate_board(board)
            # Store the evaluation in the transposition table
            self.transposition_table[board_hash] = evaluation
            return evaluation, None

        best_evaluation = float('-inf') if is_white else float('inf')
        best_move = None
        valid_moves = self.get_valid_moves("white", board) if is_white else self.get_valid_moves("black", board)

        # Ensure there are valid moves
        if not valid_moves:
            return self.evaluate_board(board), None  # Return evaluation if no moves are available

        # Move Ordering: sort valid moves based on their impact
        ordered_moves = self.order_moves(valid_moves, board)

        for piece, move in ordered_moves:
            temp_board = copy.deepcopy(board)
            row, col = piece.current_square.location
            temp_piece = temp_board.squares[row][col].piece

            self.execute_ai_move(temp_piece, move, temp_board)
            evaluation, _ = self.minimax(temp_board, depth - 1, not is_white, alpha, beta)

            # Update best evaluation and move
            if is_white:
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = (piece, move)
                alpha = max(alpha, best_evaluation)
            else:
                if evaluation < best_evaluation:
                    best_evaluation = evaluation
                    best_move = (piece, move)
                beta = min(beta, best_evaluation)

            # Alpha-Beta Pruning:
            if beta <= alpha:
                break

        # Ensure best_move is always set to a valid move
        if best_move is None:
            best_move = ordered_moves[0][:2]  # Default to the first valid move if no better one is found

        # Store the evaluation in the transposition table before returning
        self.transposition_table[board_hash] = best_evaluation

        return best_evaluation, best_move

    ###########################################################
    """ AI selects and executes a valid move directly on the real game board. """
    def handle_ai_turn(self):
        # Call minimax to get the best score and the best move (piece and its destination)
        is_white = True if self.color == "white" else False
        depth = 3
        _, best_move = self.minimax(self.game.board, depth, is_white)

        # this condition should not exist. meaning that minimax sometimes returns a bad move
        if best_move:
            piece, location = best_move
            # Execute the best move directly on the real game board
            self.execute_ai_move(piece, location, self.game.board)

        # Check if the game is finished after the move
        self.game.finished = self.game.board.check_board_state()

        if not self.game.finished:
            # Switch turns if the game is not over
            self.game.board.switch_turn()
        else:
            # Play sound if the game is finished
            pygame.mixer.Sound(f'sounds/{self.game.board.sound}.mp3').play()

        # Save the game state
        self.game.save_board_state()

        # Print for debugging
        print(self.evaluate_board(self.game.board))
