import random
from game import Game
from config import config
from history import History

class MatchBase:
    """
    Abstract base class for a match, containing common functionality
    and attributes across different match types.
    """
    
    def __init__(self, strategies, history):
        """
        Initializes the match with a list of strategies and a history instance.

        Args:
            strategies (list): List of strategy instances participating in the match.
            history (History): An instance of History to track moves.
        """
        self.strategies = strategies
        self.history = history
        self.results = {}
        self.pairing_rounds = 0
        self.performance_stats = {s.id: {"wins": 0, "games": 0} for s in strategies}

    def play_match(self):
        """To be implemented by subclasses for each match type."""
        raise NotImplementedError("Subclasses must implement `play_match`.")

    def _update_results(self, game):
        """
        Updates cumulative results from a single game round based on results in `game`.
        """
        game_results = game.get_results()

        # Update results and performance stats for pairing adjustments
        for player_id, result in game_results.items():
            if player_id not in self.results:
                # Initialize player's result dictionary with required keys
                self.results[player_id] = {
                    "strategy_id": result["strategy_id"],
                    "strategy_abbr": result["strategy_abbr"],
                    "wins": 0,
                    "draws": 0,
                    "losses": 0
                }
            # Accumulate wins, draws, and losses
            self.results[player_id]["wins"] += result["wins"]
            self.results[player_id]["draws"] += result["draws"]
            self.results[player_id]["losses"] += result["losses"]

            # Update performance stats for pairing adjustment
            self.performance_stats[player_id]["wins"] += result["wins"]
            self.performance_stats[player_id]["games"] += result["wins"] + result["losses"] + result["draws"]

    def get_match_results(self):
        """Returns the cumulative match results."""
        return self.results

    def get_performance_sorted_strategies(self):
        """
        Sorts strategies by win rate, used for performance-based pairing adjustments.

        Returns:
            list: Sorted list of strategies based on performance.
        """
        return sorted(
            self.strategies,
            key=lambda s: self.performance_stats[s.id]["wins"] / max(1, self.performance_stats[s.id]["games"]),
            reverse=True
        )

    def adjust_pairings(self):
        """
        Adjusts pairings based on strategy performance, pairing high-performance with lower-performance strategies.

        Returns:
            list of tuples: List of paired strategies.
        """
        sorted_strategies = self.get_performance_sorted_strategies()
        pairings = []
        mid_index = len(sorted_strategies) // 2
        for i in range(len(sorted_strategies)):
            if i < mid_index:
                opponent = sorted_strategies[i + mid_index]
            else:
                opponent = sorted_strategies[i - mid_index]
            pairings.append((sorted_strategies[i], opponent))
        return pairings

    def get_pairings(self):
        """
        Determines pairings for the match. Uses performance-based pairing if enabled.

        Returns:
            list of tuples: Pairings of strategy instances.
        """
        if config["match"]["pairing"]["performance_based"] and self.pairing_rounds >= config["match"]["pairing"]["adjustment_interval"]:
            # Adjust pairings based on performance
            return self.adjust_pairings()
        else:
            # Standard round-robin pairing logic
            return [(s1, s2) for i, s1 in enumerate(self.strategies) for j, s2 in enumerate(self.strategies) if i < j]


class RoundRobinMatch(MatchBase):
    """
    A round-robin match where each strategy plays against every other strategy.
    """

    def play_match(self):
        """Executes all games in a round-robin format and updates results."""
        self.pairing_rounds += 1
        pairings = self.get_pairings()
        for strategy1, strategy2 in pairings:
            game = Game(players=[strategy1, strategy2], history=self.history)
            game.play_round()
            self._update_results(game)


class SingleEliminationMatch(MatchBase):
    """
    A single-elimination match where pairs compete in each round,
    with losers eliminated until only one strategy remains.
    """

    def play_match(self):
        """Plays a single-elimination tournament and updates results."""
        remaining_strategies = self.strategies.copy()
        
        while len(remaining_strategies) > 1:
            next_round_strategies = []
            for i in range(0, len(remaining_strategies), 2):
                if i + 1 < len(remaining_strategies):
                    game = Game(players=[remaining_strategies[i], remaining_strategies[i + 1]], history=self.history)
                    game.play_round()
                    winner = self._determine_winner(game)
                    next_round_strategies.append(winner)
                else:
                    next_round_strategies.append(remaining_strategies[i])  # Auto-advance odd player
            remaining_strategies = next_round_strategies

        # Update final results with the last remaining strategy (the winner)
        if remaining_strategies:
            self._update_results(Game(players=[remaining_strategies[0]], history=self.history))

    def _determine_winner(self, game):
        """Returns the strategy with the highest win count in a game."""
        results = game.get_results()
        winner_id = max(results, key=lambda pid: results[pid]["wins"])
        return next((s for s in self.strategies if s.id == winner_id), None)


def load_match_class():
    """
    Dynamically loads the match class based on configuration in `config`.

    Returns:
        MatchBase: An instance of the specified match class.
    """
    match_type = config["match"]["default_type"]
    module_name = "match"
    # Convert to CamelCase
    class_name = ''.join(word.capitalize() for word in match_type.split('-')) + "Match"

    module = __import__(module_name)
    match_class = getattr(module, class_name)
    return match_class
