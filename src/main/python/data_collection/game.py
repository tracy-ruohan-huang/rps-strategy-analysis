# game.py

from history import History
from strategies import StrategyBase
import random
from config import config

class Game:
    """
    Represents a single game of Rock-Paper-Scissors with multiple players.
    """

    def __init__(self, players, history):
        """
        Initialize the game with a list of players and a shared history.

        Args:
            players (list): List of strategy instances representing each player.
            history (History): The history object that tracks moves.
        """
        self.players = players
        self.history = history
        self.multiple_winners_allowed = config["game"]["multiple_winners_allowed"]
        
        # Ensure each player has required identifiers and attributes
        self.results = {
            player.id: {
                "strategy_id": player.id,
                "strategy_abbr": player.abbr,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }
            for player in self.players if hasattr(player, "id") and hasattr(player, "abbr")
        }

    def select_opponent(self, player_id):
        """
        Randomly selects an opponent for a player, ensuring the opponent is not the player themselves.
        
        Args:
            player_id (int): The ID of the player for whom to select an opponent.
        
        Returns:
            int: The selected opponent's player ID.
        """
        other_players = [player.id for player in self.players if player.id != player_id]
        # If no other players, return player_id for self-pairing
        return random.choice(other_players) if other_players else player_id

    @staticmethod
    def determine_winner(player_moves, multiple_winners_allowed):

        move_hierarchy = ["rock", "scissors", "paper"]
    
        # Filter valid moves and log invalid ones
        valid_moves = {player_id: move for player_id, move in player_moves if move in move_hierarchy}
        invalid_moves = [move for _, move in player_moves if move not in move_hierarchy]
        if invalid_moves:
            print(f"Warning: Invalid moves detected {invalid_moves}. Ignoring these in winner calculation.")

        # Get unique moves
        unique_moves = set(valid_moves.values())
        if len(unique_moves) == 1:
            return []  # All players draw

        # Determine winners based on index positions
        player_positions = {player_id: move_hierarchy.index(move) for player_id, move in valid_moves.items()}
        min_position = min(player_positions.values())
        top_players = [player_id for player_id, pos in player_positions.items() if pos == min_position]

        return top_players if multiple_winners_allowed or len(top_players) == 1 else []

    def play_round(self):
        """
        Plays a round between all players and updates each player's win, draw, and loss counts.
        
        Notes:
            - Each player selects a move based on their strategy (calling their `choose` method).
            - Winners are determined based on the `multiple_winners_allowed` setting.
        """
        # player_moves = {}
        player_moves = []
        for player in self.players:
            opponent_id = self.select_opponent(player.id)
            move = player.choose(opponent_id=opponent_id, history=self.history)
            # player_moves[player.id] = move
            player_moves.append((player.id, move))  # Append each move as a tuple
        # Convert player_moves dictionary to a list of tuples and record moves to history
        # moves_list = [(player_id, move) for player_id, move in player_moves.items()]
        # self.history.record_moves(moves_list)
        
        # Record moves to history
        self.history.record_moves(player_moves)

        # Determine winners
        winners = self.determine_winner(player_moves, self.multiple_winners_allowed)

        # Update results for all players
        for player_id in self.results:
            if winners:  # If there are winners
                if player_id in winners:
                    self.results[player_id]["wins"] += 1
                else:
                    self.results[player_id]["losses"] += 1
            else:
                self.results[player_id]["draws"] += 1  # No winners, everyone draws

    def get_results(self):
        """
        Returns the raw results of the game without any calculated rates.

        Returns:
            dict: Summary of wins, draws, and losses for each player.
        """
        return self.results
