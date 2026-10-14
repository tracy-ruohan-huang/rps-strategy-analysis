import random
from config import config
from rps_core import ROCK, PAPER, SCISSORS, MOVES, DEFAULT_CONSTANT_MOVE, get_winning_move, get_losing_move, choose_random_move
from typing import List, Dict

class Strategy:
    """Base class for all strategies with access to structured game history."""

    def __init__(self, id: int, name: str, abbr: str):
        self.id = id
        self.name = name
        self.abbr = abbr

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        """
        Determines the move based on self and opponent history.
        
        Parameters:
        - self_history (List[str]): List of moves made by this player.
        - opponent_history (Dict[str, List[str]]): Dictionary where keys are opponent IDs (as strings, e.g., 'PL01'),
          and values are lists of their moves.

        Returns:
        - str: Chosen move (one of ROCK, PAPER, or SCISSORS).
        """
        raise NotImplementedError("This method should be overridden by subclasses")


class RandomStrategy(Strategy):
    """Chooses a move randomly each round."""

    def __init__(self):
        super().__init__(id=1, name="Random", abbr="Rndm")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        return choose_random_move()


class ConstantStrategy(Strategy):
    """Always plays the same move."""

    def __init__(self, move: str = DEFAULT_CONSTANT_MOVE):
        super().__init__(id=2, name="Constant", abbr="Const")
        self.move = move

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        return self.move


class SequentialStrategy(Strategy):
    """Cycles through moves in a set order: ROCK -> PAPER -> SCISSORS."""

    def __init__(self):
        super().__init__(id=3, name="Sequential", abbr="Seq")
        self.index = 0

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        move = MOVES[self.index]
        self.index = (self.index + 1) % len(MOVES)
        return move


class MirrorStrategy(Strategy):
    """Plays the opponent's last move."""

    def __init__(self):
        super().__init__(id=4, name="Mirror", abbr="Mirr")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        recent_moves = [moves[-1] for moves in opponent_history.values() if moves]
        return random.choice(recent_moves) if recent_moves else choose_random_move()


class ExclusionStrategy(Strategy):
    """Excludes the opponent's last move and picks from the other two."""

    def __init__(self):
        super().__init__(id=5, name="Exclusion", abbr="Excl")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        recent_moves = [moves[-1] for moves in opponent_history.values() if moves]
        available_moves = [move for move in MOVES if move not in recent_moves]
        return random.choice(available_moves) if available_moves else choose_random_move()


class ReactionStrategy(Strategy):
    """Counters the opponent's previous move with the winning move."""

    def __init__(self):
        super().__init__(id=6, name="Reaction", abbr="React")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        recent_moves = [moves[-1] for moves in opponent_history.values() if moves]
        if not recent_moves:
            return choose_random_move()
        last_move = random.choice(recent_moves)
        return get_winning_move(last_move)


class ReverseMirrorStrategy(Strategy):
    """Plays a move that would lose to the opponent's last move."""

    def __init__(self):
        super().__init__(id=7, name="Reverse Mirror", abbr="RevMirr")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        recent_moves = [moves[-1] for moves in opponent_history.values() if moves]
        if not recent_moves:
            return choose_random_move()
        last_move = random.choice(recent_moves)
        return get_losing_move(last_move)


class ProbabilityWeightedStrategy(Strategy):
    """Chooses moves based on the opponent's move history frequencies."""

    def __init__(self):
        super().__init__(id=8, name="Probability Weighted", abbr="ProbWt")

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        move_counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}
        for moves in opponent_history.values():
            for move in moves:
                move_counts[move] += 1
        total = sum(move_counts.values())
        if total == 0:
            return choose_random_move()
        weights = [move_counts[ROCK] / total, move_counts[PAPER] / total, move_counts[SCISSORS] / total]
        return random.choices(MOVES, weights=weights, k=1)[0]


class MultiRoundObservationStrategy(Strategy):
    """Analyzes recent move patterns in opponent's history."""

    def __init__(self, observation_window: int = config["strategy"]["observation_window"]):
        super().__init__(id=9, name="Multi-Round Observation", abbr="MRO")
        self.observation_window = observation_window

    def decide_move(self, self_history: List[str], opponent_history: Dict[str, List[str]]) -> str:
        recent_moves = []
        for moves in opponent_history.values():
            recent_moves.extend(moves[-self.observation_window:])
        if not recent_moves:
            return choose_random_move()
        most_common_move = max(set(recent_moves), key=recent_moves.count)
        return get_winning_move(most_common_move)
