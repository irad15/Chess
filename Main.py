from Game import Game
from GraphicsManager import GraphicsManager


def main():
    # Create an instance of the GraphicsManager to show the viewing angle selection
    graphics_manager = GraphicsManager()

    # Create an instance of the Game class with the selected viewing angle
    game = Game(graphics_manager)

    # Start the game
    game.run_game()


if __name__ == "__main__":
    main()
