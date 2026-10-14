# strategies.py
import importlib
import inspect
import random
import config as config
from history import History  # Ensure History is initialized in the simulation

# Constants for moves
ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
MOVES = [ROCK, PAPER, SCISSORS]

class StrategyBase:
    """
    Base class for all strategies with access to centralized history.
    """
    def __init__(self, id, name, abbr):
        self.id = id
        self.name = name
        self.abbr = abbr

    def choose(self, opponent_id, history):
        """
        Selects a move for this strategy, using history to inform decisions.
        This method should be overridden in subclasses.
        
        Args:
            opponent_id (int): The ID of the selected opponent.
            history (History): Centralized history instance.
            
        Returns:
            str: Selected move.
        """
        raise NotImplementedError("Subclasses should implement this method")


class RandomStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=0, name="Random", abbr="Rndm")

    def choose(self, opponent_id, history):
        return random.choice(MOVES)

#class ConstantStrategy(StrategyBase):
#    def __init__(self, constant_move=ROCK):
#        super().__init__(id=1, name="Constant", abbr="Const")
#        self.constant_move = constant_move
#
#    def choose(self, opponent_id, history):
#        return self.constant_move

class SequentialStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=2, name="Sequential", abbr="Seq")

    def choose(self, opponent_id, history):
        player_history = history.get_player_history(self.id)
        if not player_history:
            return ROCK
        last_move = player_history[-1]
        return MOVES[(MOVES.index(last_move) + 1) % len(MOVES)]


class MirrorStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=3, name="Mirror", abbr="Mirr")

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)
        if not opponent_history:
            return random.choice(MOVES)
        return opponent_history[-1]


class ExclusionStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=4, name="Exclusion", abbr="Excl")

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)
        if not opponent_history:
            return random.choice(MOVES)
        last_opponent_move = opponent_history[-1]
        return random.choice([move for move in MOVES if move != last_opponent_move])


class ReactionStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=5, name="Reaction", abbr="React")

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)
        if not opponent_history:
            return random.choice(MOVES)
        last_opponent_move = opponent_history[-1]
        if last_opponent_move == ROCK:
            return PAPER
        elif last_opponent_move == PAPER:
            return SCISSORS
        elif last_opponent_move == SCISSORS:
            return ROCK


class ReverseMirrorStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=6, name="Reverse Mirror", abbr="RevMirr")

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)
        if not opponent_history:
            return random.choice(MOVES)
        last_opponent_move = opponent_history[-1]
        if last_opponent_move == ROCK:
            return SCISSORS
        elif last_opponent_move == PAPER:
            return ROCK
        elif last_opponent_move == SCISSORS:
            return PAPER


class ProbabilityWeightedStrategy(StrategyBase):
    def __init__(self):
        super().__init__(id=7, name="Probability-Weighted", abbr="ProbWt")

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)
        if not opponent_history:
            return random.choice(MOVES)
        count_rock = opponent_history.count(ROCK)
        count_paper = opponent_history.count(PAPER)
        count_scissors = opponent_history.count(SCISSORS)
        total = len(opponent_history)
        prob_rock = count_rock / total
        prob_paper = count_paper / total
        prob_scissors = count_scissors / total
        return random.choices(MOVES, weights=[prob_paper, prob_scissors, prob_rock])[0]


class MultiRoundObservationStrategy(StrategyBase):
    def __init__(self, rounds_to_observe=5):
        super().__init__(id=8, name="Multi-Round Observation", abbr="MRO")
        self.rounds_to_observe = rounds_to_observe

    def choose(self, opponent_id, history):
        opponent_history = history.get_player_history(opponent_id)[-self.rounds_to_observe:]
        if len(opponent_history) < self.rounds_to_observe:
            return random.choice(MOVES)
        count_rock = opponent_history.count(ROCK)
        count_paper = opponent_history.count(PAPER)
        count_scissors = opponent_history.count(SCISSORS)
        if count_rock > count_paper and count_rock > count_scissors:
            return PAPER
        elif count_paper > count_rock and count_paper > count_scissors:
            return SCISSORS
        elif count_scissors > count_rock and count_scissors > count_paper:
            return ROCK
        return random.choice(MOVES)
    
class MultiRoundObservation2Strategy(StrategyBase):
    def __init__(self):
        super().__init__(id=9, name="Multi-Round Observation 2", abbr="MRO2")

    def choose(self, opponent_id, history):
        # Retrieve the opponent's last moves based on the configured history length
        opponent_history = history.get_player_history(opponent_id)
        
        if not opponent_history:
            return random.choice(MOVES)  # Choose randomly if no history

        # Weighted counting of opponent's moves, more recent moves have higher weight
        weights = [i + 1 for i in range(len(opponent_history))]
        count_rock = sum(w for move, w in zip(opponent_history, weights) if move == ROCK)
        count_paper = sum(w for move, w in zip(opponent_history, weights) if move == PAPER)
        count_scissors = sum(w for move, w in zip(opponent_history, weights) if move == SCISSORS)

        # Decide based on the weighted count
        if count_rock > count_paper and count_rock > count_scissors:
            return PAPER  # Counter rock
        elif count_paper > count_rock and count_paper > count_scissors:
            return SCISSORS  # Counter paper
        elif count_scissors > count_rock and count_scissors > count_paper:
            return ROCK  # Counter scissors
        else:
            # If counts are tied, play the counter to the last move
            last_move = opponent_history[-1]
            if last_move == ROCK:
                return PAPER
            elif last_move == PAPER:
                return SCISSORS
            else:
                return ROCK

def load_strategies(module_name="strategies"):
    """
    Dynamically loads all subclasses of Strategy from the specified module.
    """
    strategy_functions = {}
    try:
        # Dynamically import the specified module
        module = importlib.import_module(module_name)

        # Iterate over all classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if the class is a subclass of Strategy and not the Strategy base class itself
            if issubclass(obj, StrategyBase) and obj is not StrategyBase:
                # Instantiate the strategy class and add it to the dictionary with its abbreviation as the key
                instance = obj()
                strategy_functions[instance.id] = instance

    except (ImportError, AttributeError) as e:
        print(f"Error loading strategies from {module_name}: {e}")

    # Sort by strategy_id and return as an ordered dictionary
    sorted_strategies = dict(sorted(strategy_functions.items()))
    return sorted_strategies
