# Chess Game with AI

This project is a Python-based chess pygame that allows players to either play against an AI bot using the minimax algorithm or in a hot seat mode (two players taking turns on the same device).

## Features

- **All chess logic works well**: including: en-passant, pawn double foreward, checks, pins, castling, pawn promotion.
- **AI opponent using Minimax Algorithm**: The AI bot is capable of playing at an intermediate level using the minimax algorithm with alpha-beta pruning.
- **Two Player Mode (Hot Seat)**: Play with a friend in a local hot seat mode.
- **Graphical User Interface**: The game is visually represented with a simple and clean Pygame interface, featuring buttons for interaction.

## Installation

1. download the repository to your local machine

2. make sure to install pygame on your machine

## How to Play

1. **Run the game**:
    ```bash
    python main.py
    ```


## Minimax Algorithm

The AI bot uses the minimax algorithm to evaluate potential moves and decide the best possible move. It performs depth-limited search with alpha-beta pruning to make it efficient while still competitive.
