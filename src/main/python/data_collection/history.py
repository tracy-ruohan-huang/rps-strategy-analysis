import csv
from collections import defaultdict
from config import config

class History:
    """
    Manages the move history for players in a centralized way, with options for
    keeping the history to a limited number of rounds and logging all moves to a file.
    """

    def __init__(self):
        self.history = defaultdict(list)  # Each player's moves are stored as a list of moves
        self.limits = config["history"]["limits"]  # Keep only the last 'h' limits
        self.store_global_history = config["history"]["store_global_history"]
        self.global_history_file = config["history"]["output"]["filename"]
        self.global_history_columns = config["history"]["output"]["columns"]

        # Initialize the log file if global history storage is enabled
        if self.store_global_history:
            self._initialize_log_file()

    def _initialize_log_file(self):
        """Initializes the global history log file with headers."""
        with open(self.global_history_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.global_history_columns)

    def record_moves(self, moves):
        """
        Records the moves made by all players in a single round.

        Args:
            moves (list of tuples): Each tuple contains (player_id, move).
        """
        # Debug check to confirm received structure
        if not isinstance(moves, list) or not all(isinstance(move, tuple) and len(move) == 2 for move in moves):
            raise ValueError("Expected 'moves' to be a list of tuples [(player_id, move), ...]")
        
        for player_id, move in moves:
            # Record move in the history with limited rounds
            self.history[player_id].append(move)
            if len(self.history[player_id]) > self.limits:
                self.history[player_id].pop(0)

            # Log move if global history storage is enabled
            if self.store_global_history:
                self._log_move(player_id, move)

    def _log_move(self, player_id, move):
        """Logs a single move to the global history file."""
        with open(self.global_history_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([player_id, move])

    def get_player_history(self, player_id, rounds=None):
        """
        Retrieves the last 'n' moves for a player, where 'n' is defined by rounds.

        Args:
            player_id (int): The player ID to get the history for.
            rounds (int): The number of past rounds to retrieve. If None, use max_rounds.

        Returns:
            list: The last `rounds` moves of the player.
        """
        rounds = rounds if rounds is not None else self.limits
        return self.history[player_id][-rounds:]

    def clear_history(self):
        """Clears the history for a new experiment if needed."""
        self.history.clear()
        if self.store_global_history:
            self._initialize_log_file()

    def get_full_history(self):
        """
        Retrieve the full move history in a simplified format.

        Returns:
            list of dicts: Full history of recorded moves.
        """
        full_history = []
        for player_id, moves in self.history.items():
           for move in moves:
               full_history.append({
                    "Player ID": player_id,
                    "Move": move
                })
        return full_history
       