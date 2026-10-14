# config.py
import os

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'

# Directory specifically for raw data
raw_data_file_path = f"{data_file_path}/raw"
# Directory specifically for processed data
processed_data_file_path = f"{data_file_path}/processed"

config = {
    "strategy": {
        "strategy_pools": {
            "default": [1, 2, 3, 4, 5, 6, 7, 8, 9], # All strategies
            "no-constant": [1, 3, 4, 5, 6, 7, 8, 9],  # All strategies for balanced matches
            "random_subset": 5  # Number of strategies randomly chosen for each simulation
        },
        "observation_window": 3  # For observation-based strategies, rounds of opponent history to observe. short (1-3), medium (5-10), long (10+)
    },
    "game": {
        "multiple_winners_allowed": 0,  # 0 for no multiple winners, 1 for allowing multiple winners in a round
        "variable_round_length": {
            "enabled": True,
            "min_rounds": 50,
            "max_rounds": 200
        },
    },
    "pairing": {
        "pair_size": 2, 
        "rule": "round-robin",  # Default match type
        "rules": {
            "round-robin": {
            },
            "single-elimination": {
                "advance_criteria": "winner"  # Winner advances to the next round
            },
        },
    },
    "simulation": {
        "logging": {
            "log_filename": f"{data_file_path}/simulation_log.txt",
            "progress_interval": 10  # Percentage intervals for logging progress updates
        },
        "output": {
            "filename": f"{data_file_path}/simulation_results.csv",
            "columns": [
                "Rnds",
                "ID", "Strategy", 
                "Wins", "Losses", "Draws", 
                "WR (%)", "DR (%)", 
                "Avg. WR (%)", "WRD (%)"
            ]
        },
        "baseline_tracking": True,  # Track a baseline win rate for CUSUM analysis
        "round_length_variability": True  # Randomize round length within min_rounds and max_rounds
    },
    "experiment": {
        "rounds_per_game": range(10, 1001, 10),  # Range of rounds per game (rpg)
        "output": {
            "match_group_perf_file": f"{raw_data_file_path}/match_group_perf.csv",  # Performance per match group for each strategy.
            "match_group_perf_processed_file": f"{processed_data_file_path}/match_group_perf_processed.csv",  # Performance per match group for each strategy.
            "match_group_perf_summary_file": f"{processed_data_file_path}/match_group_perf_summary.csv",  # Aggregated performance per match group for each strategy.
            "strategy_perf_file": f"{processed_data_file_path}/strategy_perf.csv",  # Overall performance for each strategy.
            "strategy_perf_summary_file": f"{processed_data_file_path}/strategy_perf_summary.csv",  # Aggregated performance across all match groups for each strategy.
        },
        "performance_columns": {
            "group_by": ["strategy_id", "strategy_abbr"],
            "owr": "OWR",
            "odr": "ODR",
            "output": ["strategy_id", "strategy_abbr", "avg_owr", "avg_odr"]
        },
  
    },
}
