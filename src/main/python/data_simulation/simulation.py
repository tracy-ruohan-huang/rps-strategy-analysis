from config import config
from strategy import Strategy
from pairing import Pairing
from game import Game
import pandas as pd

class Simulation:
    def __init__(self, strategy_pool_name, rounds_per_game=100):
        """
        Initializes the Simulation instance with a selected strategy pool.
        :param strategy_pool_name: Name of the strategy pool to use (e.g., 'balanced', 'aggressive').
        :param rounds_per_game: Number of rounds each pairing should play.
        """
        self.strategy_pool_name = strategy_pool_name
        self.rounds_per_game = rounds_per_game
        self.strategies = self.load_strategies()
        self.results_pr = []  # Store PR (Pairing Results) for each game in the simulation
        self.results_or = pd.DataFrame()  # Store OR (Overall Results) after aggregation

    def load_strategies(self):
        """Dynamically loads strategies based on the selected pool from config."""
        pool_ids = config["strategy"]["strategy_pools"].get(self.strategy_pool_name, [])
        strategies = []

        # Fetch all Strategy subclasses in strategy.py
        strategy_classes = {cls().id: cls for cls in Strategy.__subclasses__()}

        # Instantiate only strategies that match the IDs in the pool
        for strategy_id in pool_ids:
            strategy_class = strategy_classes.get(strategy_id)
            if strategy_class:
                strategies.append(strategy_class())

        return strategies

    def run(self):
        """Runs the simulation, generating pairs and executing games."""
        # Generate pairings from the shared strategies
        pairing = Pairing(strategies=self.strategies, pair_size=2, rule="round-robin")
        pairs = pairing.generate_pairs()

        # Run games for each pair and collect results
        for pid, strategy_pair in pairs:
            game = Game(pid=pid, strategies=strategy_pair, rounds=self.rounds_per_game)
            game_results = game.play()
            
            # Calculate PDR for each player in the game results
            for result in game_results:
                total_rounds = result['rpg']
                draw_rate = (result['draws'] / total_rounds) * 100 if total_rounds > 0 else 0
                result['pdr'] = round(draw_rate, 2)  # Pairing Draw Rate
                
            self.results_pr.extend(game_results)  # Append each game result to results_pr

        # Calculate OR for each strategy after all games
        self.results_or = self.aggregate_or()

    def output_pr_results(self, filename="simulation_pr_result.csv"):
        """Outputs the Pairing Results (PR) to a CSV file."""
        # Convert PR results to a DataFrame for easier handling and export
        pr_df = pd.DataFrame(self.results_pr)
        pr_df.to_csv(filename, index=False)
        print(f"Pairing Results (PR) with PWR and PDR saved to {filename}")

    def output_or_results(self, filename="simulation_or_result.csv"):
        """Outputs the Overall Results (OR) to a CSV file."""
        self.results_or.to_csv(filename, index=False)
        print(f"Overall Results (OR) with OWR and ODR saved to {filename}")

    def aggregate_or(self):
        """Calculates the Overall Win Rate (OWR) and Overall Draw Rate (ODR) for each strategy across the simulation."""
        results_df = pd.DataFrame(self.results_pr)

        # Aggregate wins, draws, and rounds for each strategy
        strategy_aggregates = results_df.groupby(['strategy_id', 'strategy_abbr']).agg(
            total_wins=('wins', 'sum'),
            total_draws=('draws', 'sum'),
            total_rounds=('rpg', 'sum')
        ).reset_index()

        # Calculate OWR as (total_wins / total_rounds) * 100
        strategy_aggregates['OWR'] = (strategy_aggregates['total_wins'] / strategy_aggregates['total_rounds']) * 100
        strategy_aggregates['OWR'] = strategy_aggregates['OWR'].round(2)  # Round to two decimal places

        # Calculate ODR as (total_draws / total_rounds) * 100
        strategy_aggregates['ODR'] = (strategy_aggregates['total_draws'] / strategy_aggregates['total_rounds']) * 100
        strategy_aggregates['ODR'] = strategy_aggregates['ODR'].round(2)  # Round to two decimal places

        # Add RPG (rounds per game) column at the beginning
        strategy_aggregates.insert(0, 'rpg', self.rounds_per_game)

        print("Overall Win Rate (OWR) and Overall Draw Rate (ODR) per strategy in the simulation:")
        print(strategy_aggregates[['rpg', 'strategy_id', 'strategy_abbr', 'OWR', 'ODR']])

        return strategy_aggregates[['rpg', 'strategy_id', 'strategy_abbr', 'OWR', 'ODR']]

# Tester function
def test_simulation():
    """Runs a test simulation and outputs results to CSV files."""
    # Initialize a simulation with a sample strategy pool and 10 rounds per game
    simulation = Simulation(strategy_pool_name="balanced", rounds_per_game=10)
    
    # Run the simulation
    simulation.run()
    
    # Output the PR results to a CSV file
    simulation.output_pr_results("test_simulation_pr_result.csv")
    
    # Output the OR results to a CSV file
    simulation.output_or_results("test_simulation_or_result.csv")

# Run the tester function
if __name__ == "__main__":
    test_simulation()
