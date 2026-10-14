import pandas as pd
from config import config

class ExperimentStatistics:
    def __init__(self):
        """Initializes the ExperimentStatistics class for computing aggregated statistics."""
        # Load match group performance data from file
        self.match_group_perf = pd.read_csv(config["experiment"]["output"]["match_group_perf_file"])
        self.filtered_data = pd.DataFrame()  # Store filtered data after applying all filters
        self.strategy_perf_summary = pd.DataFrame()  # Store aggregated strategy performance summary
        self.match_group_perf_summary = pd.DataFrame()  # Store aggregated match group performance summary
        self.strategy_performance = pd.DataFrame()  # Store detailed strategy performance

    def filter_data(self):
        """
        Applies centralized data filtering logic, including:
        1. Removing self-pairing records (where identical mg_id and strategy_id pairs exist across rows).
        2. Applying a data range filter based on the 5th to 95th percentiles of `pwr`.
        """
        # Step 1: Remove self-pairing records (where both mg_id and strategy_id are duplicated)
        non_self_pairing = self.match_group_perf[~self.match_group_perf.duplicated(subset=['mg_id', 'strategy_id', 'rpg'], keep=False)]

        # Debug: Check if non_self_pairing is empty
        if non_self_pairing.empty:
            print("After removing self-pairing records, data is empty.")
            return

        # Step 2: Calculate 5th and 95th percentiles for `pwr` in the filtered data
        pwr_5th_percentile = 0 # non_self_pairing['pwr'].quantile(0.05)
        pwr_95th_percentile = 100 # non_self_pairing['pwr'].quantile(0.95)
        
        # Step 3: Apply the percentile range filter to the non-self-pairing data
        pwr_range_filter = non_self_pairing['pwr'].between(pwr_5th_percentile, pwr_95th_percentile)
        self.filtered_data = non_self_pairing[pwr_range_filter]

        # Final debugging output
        print(f"Data filtered to exclude self-pairing records.")
        print(f"Applying pwr range filter between {pwr_5th_percentile:.2f} and {pwr_95th_percentile:.2f}.")
        print(f"Filtered data contains {len(self.filtered_data)} records.")
       
    def aggregate_strategy_perf_summary(self) -> None:
        """Calculates the summary of OWR and ODR for each strategy based on `strategy_performance`."""
        # Ensure that strategy_performance is calculated
        if self.strategy_performance.empty:
            print("Strategy performance data is empty. Please ensure `calculate_strategy_performance()` is called first.")
            return
        
        # Group by strategy to calculate summary statistics for OWR and ODR
        aggregated = self.strategy_performance.groupby(['strategy_id', 'strategy_abbr']).agg(
            total_wins=('total_wins', 'sum'),
            total_draws=('total_draws', 'sum'),
            total_rounds=('total_rounds', 'sum'),
            owr_mean=('owr', 'mean'),
            owr_max=('owr', 'max'),
            owr_min=('owr', 'min'),
            owr_std=('owr', 'std'),
            owr_median=('owr', 'median'),
            odr_mean=('odr', 'mean'),
            odr_max=('odr', 'max'),
            odr_min=('odr', 'min'),
            odr_std=('odr', 'std'),
            odr_median=('odr', 'median')
        ).reset_index()

        # Calculate experiment-level OWR and ODR
        aggregated['owr'] = (aggregated['total_wins'] / aggregated['total_rounds']) * 100
        aggregated['odr'] = (aggregated['total_draws'] / aggregated['total_rounds']) * 100

        # Round results for clarity
        aggregated = aggregated.round(2)

        # Assign the final aggregated result to `strategy_perf_summary`
        self.strategy_perf_summary = aggregated

    def aggregate_match_group_perf_summary(self) -> None:
        """Calculates the aggregated statistics for match group performance after filtering."""
        aggregated = self.filtered_data.groupby(['mg_id', 'strategy_id', 'strategy_abbr']).agg(
            total_wins=('wins', 'sum'),
            total_draws=('draws', 'sum'),
            total_rounds=('rpg', 'sum'),
            pwr_mean=('pwr', 'mean'),
            pwr_max=('pwr', 'max'),
            pwr_min=('pwr', 'min'),
            pwr_std=('pwr', 'std'),
            pwr_median=('pwr', 'median'),
            pdr_mean=('pdr', 'mean'),
            pdr_max=('pdr', 'max'),
            pdr_min=('pdr', 'min'),
            pdr_std=('pdr', 'std'),
            pdr_median=('pdr', 'median')
        ).reset_index()

        # Round results for clarity
        aggregated = aggregated.round(2)

        # Assign the final aggregated result to match_group_perf_summary
        self.match_group_perf_summary = aggregated

    def calculate_strategy_performance(self) -> None:
        """Calculates overall strategy performance metrics within each simulation (rpg) across all match groups."""
        # Group by `strategy_id`, `strategy_abbr`, and `rpg` to sum wins, draws, and rounds across all match groups
        strategy_performance = self.filtered_data.groupby(['strategy_id', 'strategy_abbr', 'rpg']).agg(
            total_wins=('wins', 'sum'),
            total_draws=('draws', 'sum'),
            total_rounds=('rpg', 'sum')
        ).reset_index()

        # Calculate overall OWR and ODR for each strategy within each simulation (rpg)
        strategy_performance['owr'] = (strategy_performance['total_wins'] / strategy_performance['total_rounds']) * 100
        strategy_performance['odr'] = (strategy_performance['total_draws'] / strategy_performance['total_rounds']) * 100

        # Round for clarity
        strategy_performance = strategy_performance.round(2)

        # Assign the detailed performance for each simulation to `self.strategy_performance`
        self.strategy_performance = strategy_performance


    def save_statistics(self) -> None:
        """Saves the aggregated statistics and filtered data to CSV files."""
        # Save filtered data as processed data
        processed_data_path = config["experiment"]["output"]["match_group_perf_processed_file"]
        self.filtered_data.to_csv(processed_data_path, index=False)

        # Save aggregated statistics
        self.strategy_perf_summary.to_csv(config["experiment"]["output"]["strategy_perf_summary_file"], index=False)
        self.match_group_perf_summary.to_csv(config["experiment"]["output"]["match_group_perf_summary_file"], index=False)
        self.strategy_performance.to_csv(config["experiment"]["output"]["strategy_perf_file"], index=False)

        print(f"Filtered data saved to {processed_data_path}")
        print("Strategy performance summary saved to", config["experiment"]["output"]["strategy_perf_summary_file"])
        print("Match group performance summary saved to", config["experiment"]["output"]["match_group_perf_summary_file"])
        print("Detailed strategy performance saved to", config["experiment"]["output"]["strategy_perf_file"])

# Tester function
def test_experiment_statistics() -> None:
    """Runs the statistics calculations on match group performance data and outputs the results."""
    # Initialize the ExperimentStatistics class
    statistics = ExperimentStatistics()
    
    # Run data filtering
    statistics.filter_data()
    
    # Run statistics calculations
    statistics.calculate_strategy_performance()
    statistics.aggregate_strategy_perf_summary()
    statistics.aggregate_match_group_perf_summary()
    
    # Output the aggregated statistics and filtered data to files
    statistics.save_statistics()

# Run the tester function
if __name__ == "__main__":
    test_experiment_statistics()
