""" Mainly important for highlighting squares and control of the Board"""


class Square:
    def __init__(self, location: tuple[int, int]):
        self.location: tuple[int, int] = location  # The (x, y) position of the square on the board
        self.piece = None  # The piece currently occupying the square, if any

    def is_occupied(self) -> bool:
        return self.piece is not None

    def remove_piece(self):
        if self.is_occupied():  # Ensure there's a piece to remove
            self.piece.current_square = None
            self.piece = None

    def set_piece(self, piece):
        piece.current_square = self  # Update the piece's reference to this square.
        self.piece = piece

    def __str__(self) -> str:
        return self.piece.image_path if self.is_occupied() else "Unoccupied"

    def __repr__(self) -> str:
        return f"Square(location={self.location}, piece={'None' if not self.piece else self.piece})"

    def __eq__(self, other) -> bool:
        return self.location == other.location
