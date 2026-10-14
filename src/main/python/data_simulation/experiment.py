import pandas as pd
from simulation import Simulation
from config import config

class Experiment:
    def __init__(self, strategy_pool_name: str, rounds_per_game_range: range):
        """
        Initializes an Experiment instance to run multiple simulations with different game rounds.
        
        Parameters:
        - strategy_pool_name (str): Name of the strategy pool to use for all simulations.
        - rounds_per_game_range (range): Range of values for the number of rounds per game (e.g., range(10, 100, 10)).
        """
        self.strategy_pool_name = strategy_pool_name
        self.rounds_per_game_range = rounds_per_game_range
        self.match_group_perf = pd.DataFrame()  # Store match group performance (PR) results from all simulations

        # Set up output path for match group performance data from config
        self.match_group_perf_file = config["experiment"]["output"]["match_group_perf_file"]

    def run(self) -> None:
        """Runs the experiment by executing multiple simulations with varying rounds per game and collecting results."""
        for rounds_per_game in self.rounds_per_game_range:
            print(f"Running simulation with rounds_per_game={rounds_per_game}...")

            # Initialize and run a simulation with the specified rounds_per_game
            simulation = Simulation(strategy_pool_name=self.strategy_pool_name, rounds_per_game=rounds_per_game)
            simulation.run()

            # Collect match group performance from each simulation
            simulation_match_group_perf_df = pd.DataFrame(simulation.results_pr)
            self.match_group_perf = pd.concat([self.match_group_perf, simulation_match_group_perf_df], ignore_index=True)

        # Save the raw match group performance for later analysis
        self.save_match_group_perf()

    def save_match_group_perf(self) -> None:
        """Saves the match group performance (raw data) to CSV."""
        self.match_group_perf.to_csv(self.match_group_perf_file, index=False)
        print(f"Match group performance data saved to {self.match_group_perf_file}")

# Tester function for Experiment
def test_experiment() -> None:
    """Runs an experiment with multiple simulations and outputs aggregated results to CSV files."""
    # Initialize an experiment with a sample strategy pool and range of rounds for each simulation
    experiment = Experiment(strategy_pool_name="default", rounds_per_game_range=config["experiment"]["rounds_per_game"])
    
    # Run the experiment
    experiment.run()

# Run the tester function if this script is executed
if __name__ == "__main__":
    test_experiment()
