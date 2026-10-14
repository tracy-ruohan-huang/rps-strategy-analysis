from match import load_match_class
from strategies import load_strategies
import csv
from history import History

class Simulation:
    """
    Runs a simulation for a specified number of rounds, involving multiple matches
    between strategies.
    """

    def __init__(self, rounds):
        self.rounds = rounds
        self.strategies = load_strategies()
        self.match_class = load_match_class()
        self.results = []
        self.history = History()  # Shared history instance for centralized tracking

    def run(self):
        """
        Runs the simulation over a fixed number of rounds and collects results.

        Returns:
            list: A list of dictionaries with the results for each strategy.
        """
        for round_num in range(self.rounds):
            print(f"Starting simulation round {round_num + 1} of {self.rounds}...")

            # Initialize match with strategies and the shared history
            match = self.match_class(strategies=list(self.strategies.values()), history=self.history)
            match.play_match()

            # Capture and aggregate the results from the match
            match_results = match.get_match_results()
            self.aggregate_results(match_results)

        # Calculate win rates, draw rates, and WRD after all rounds
        self.calculate_statistics()
        return self.results

    def aggregate_results(self, match_results):
        """
        Aggregates results across matches by updating each strategy’s state.

        Args:
            match_results (dict): The results of the current match.
        """
        for player_id, result in match_results.items():
            # Check if player results already exist in self.results
            existing_result = next((res for res in self.results if res["strategy_id"] == player_id), None)

            if existing_result:
                # Update existing results
                existing_result["wins"] += result["wins"]
                existing_result["draws"] += result["draws"]
                existing_result["losses"] += result["losses"]
            else:
                # Add new entry if not present in self.results
                self.results.append({
                    "simulation_rounds": self.rounds,
                    "strategy_id": result["strategy_id"],
                    "strategy_abbr": result["strategy_abbr"],
                    "wins": result["wins"],
                    "draws": result["draws"],
                    "losses": result["losses"],
                })

    def calculate_statistics(self):
        """
        Calculates the win rate, draw rate, and Win Rate Difference (WRD) for each strategy.
        """
        total_games = sum(res["wins"] + res["draws"] + res["losses"] for res in self.results)

        # Calculate win and draw rates, WRD
        for result in self.results:
            total_played = result["wins"] + result["draws"] + result["losses"]
            result["win_rate"] = (result["wins"] / total_played) * 100 if total_played > 0 else 0.0
            result["draw_rate"] = (result["draws"] / total_played) * 100 if total_played > 0 else 0.0
            avg_win_rate = (sum(res["wins"] for res in self.results) / total_games) * 100 if total_games > 0 else 0.0
            result["avg_win_rate"] = avg_win_rate
            result["wrd"] = result["win_rate"] - avg_win_rate

    def output_to_csv(self, filename):
        """
        Outputs the simulation results to a CSV file.

        Args:
            filename (str): The name of the file to write to.
        """
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["simulation_rounds", "strategy_id", "strategy_abbr", "wins", "draws", "losses", "win_rate", "draw_rate", "wrd"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

