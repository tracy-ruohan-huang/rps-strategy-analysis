from rps_core import compare_moves

class Player:
    """Represents a player using a specific strategy in the game."""
    def __init__(self, player_instance_id, strategy):
        self.player_instance_id = player_instance_id  # e.g., 'PL1'
        self.strategy = strategy
        self.history = []  # Stores the player's own move history

    def decide_move(self, self_history, opponent_history):
        """Calls the strategy's decide_move method."""
        move = self.strategy.decide_move(self_history, opponent_history)
        self.history.append(move)  # Record move in player's own history
        return move

class Game:
    def __init__(self, pid, strategies, rounds):
        """
        Initializes the Game instance.
        :param pid: Unique pairing ID for the set of strategies.
        :param strategies: List of Strategy instances for this game.
        :param rounds: Number of rounds each pairing should play.
        """
        self.pid = pid  # e.g., '01' for pairing of strategies 0 and 1
        # Use 'PL' prefix for player_instance_id to differentiate from pid
        self.players = [Player(player_instance_id=f"PL{i}", strategy=strategy) for i, strategy in enumerate(strategies)]
        self.rounds = rounds
        self.game_history = []  # Cumulative history of all rounds
        self.results = []  # Stores results for PWR calculation

    def play(self):
        """Plays the game for the specified number of rounds and records results."""
        # Initialize individual scores for each player
        scores = {player.player_instance_id: {'wins': 0, 'draws': 0, 'losses': 0} for player in self.players}

        for _ in range(self.rounds):
            moves = {}
            for player in self.players:
                self_history, opponent_history = self.get_structured_history(player.player_instance_id)
                move = player.decide_move(self_history, opponent_history)
                moves[player.player_instance_id] = move

            # Track outcomes for each round
            processed_pairs = set()
            for player in self.players:
                for opponent in self.players:
                    if player.player_instance_id == opponent.player_instance_id:
                        continue
                    
                    # Ensure each pairing is only processed once per round
                    pair_key = tuple(sorted([player.player_instance_id, opponent.player_instance_id]))
                    if pair_key in processed_pairs:
                        continue
                    processed_pairs.add(pair_key)

                    result = compare_moves(moves[player.player_instance_id], moves[opponent.player_instance_id])

                    # Update scores based on the result
                    if result == 1:
                        scores[player.player_instance_id]['wins'] += 1
                        scores[opponent.player_instance_id]['losses'] += 1
                    elif result == -1:
                        scores[player.player_instance_id]['losses'] += 1
                        scores[opponent.player_instance_id]['wins'] += 1
                    elif result == 0:
                        # Count draw for both players in this round
                        scores[player.player_instance_id]['draws'] += 1
                        scores[opponent.player_instance_id]['draws'] += 1

            # Record this round's moves in the history for reference in future rounds
            self.game_history.append(moves)

        # Store results after the game is complete, setting rounds explicitly
        for player in self.players:
            self.update_results(player, scores)

        return self.results

    def update_results(self, player, score):
        """Updates the results with pid-based records for PWR calculation."""
        total_rounds = self.rounds  # Use the fixed rounds value from game configuration
        player_scores = score[player.player_instance_id]  # Individual player scores

        # Calculate PWR as a percentage based on this player's wins
        pwr = (player_scores['wins'] / total_rounds) * 100 if total_rounds > 0 else 0  

        self.results.append({
            'mg_id': self.pid,
            'rpg': total_rounds,  # Fixed rounds per game
            'player_id': player.player_instance_id,
            'strategy_id': player.strategy.id,
            'strategy_abbr': player.strategy.abbr,
            'wins': player_scores['wins'],
            'draws': player_scores['draws'],
            'pwr': round(pwr, 2)  # Pairing Win Rate in percentage, rounded to 2 decimal places
        })

    def get_structured_history(self, player_instance_id):
        """Returns structured history for a given player, separating self and opponent history."""
        self_history = []
        opponent_history = {opponent.player_instance_id: [] for opponent in self.players if opponent.player_instance_id != player_instance_id}

        for round_data in self.game_history:
            if player_instance_id in round_data:
                self_history.append(round_data[player_instance_id])
            for opponent_id in opponent_history:
                if opponent_id in round_data:
                    opponent_history[opponent_id].append(round_data[opponent_id])

        return self_history, opponent_history
