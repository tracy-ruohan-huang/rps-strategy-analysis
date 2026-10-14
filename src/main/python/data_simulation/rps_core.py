import random

# Constants for moves
ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
MOVES = [ROCK, PAPER, SCISSORS]
DEFAULT_CONSTANT_MOVE = ROCK

# Move outcome mapping for comparisons
MOVE_OUTCOMES = {
    ROCK: {SCISSORS: 1, ROCK: 0, PAPER: -1},
    PAPER: {ROCK: 1, PAPER: 0, SCISSORS: -1},
    SCISSORS: {PAPER: 1, SCISSORS: 0, ROCK: -1}
}

# Mappings for winning and losing moves
WINNING_MOVE = {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}
LOSING_MOVE = {ROCK: SCISSORS, PAPER: ROCK, SCISSORS: PAPER}

def compare_moves(move1: str, move2: str) -> int:
    """
    Compares two moves and returns:
        1 if move1 wins,
       -1 if move1 loses,
        0 if it's a draw.

    Parameters:
    - move1: str, one of ROCK, PAPER, or SCISSORS
    - move2: str, one of ROCK, PAPER, or SCISSORS

    Returns:
    - int: Result of the comparison (1, -1, or 0)
    """
    if move1 not in MOVES or move2 not in MOVES:
        raise ValueError("Invalid moves provided.")
    return MOVE_OUTCOMES[move1][move2]

def get_winning_move(move: str) -> str:
    """
    Returns the move that beats the given move.

    Parameters:
    - move: str, one of ROCK, PAPER, or SCISSORS

    Returns:
    - str: The move that would win against the provided move
    """
    if move not in WINNING_MOVE:
        raise ValueError("Invalid move provided.")
    return WINNING_MOVE[move]

def get_losing_move(move: str) -> str:
    """
    Returns the move that would lose to the given move.

    Parameters:
    - move: str, one of ROCK, PAPER, or SCISSORS

    Returns:
    - str: The move that would lose against the provided move
    """
    if move not in LOSING_MOVE:
        raise ValueError("Invalid move provided.")
    return LOSING_MOVE[move]

def is_valid_move(move: str) -> bool:
    """
    Checks if a move is valid.

    Parameters:
    - move: str, the move to check

    Returns:
    - bool: True if the move is valid, False otherwise
    """
    return move in MOVES

def choose_random_move() -> str:
    """
    Chooses a random move from the available options.

    Returns:
    - str: A randomly selected move
    """
    return random.choice(MOVES)
