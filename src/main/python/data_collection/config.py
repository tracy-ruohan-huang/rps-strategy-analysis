# config.py
import os

base_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
data_file_path = os.path.join(base_file_path, 'data')
result_file_path = os.path.join(base_file_path, 'results')

config = {
    "strategy": {
        "strategies": [
            # Add more strategies as needed
        ],
        "strategy_pools": {
            "balanced": [0, 1, 2, 3, 4, 5, 6, 7, 8],  # All strategies for balanced matches
            "random_subset": 5  # Number of strategies randomly chosen for each simulation
        },
        "opponent_selection": {
            "type": "weighted",  # Options: 'weighted', 'random'
            "weighting_factor": 0.5  # Proportion favoring high-performing strategies for pairing
        },
        "round_observation_window": 5  # For observation-based strategies, rounds of opponent history to observe
    },
    "game": {
        "num_players": 2,  # Default number of players per game
        "multiple_winners_allowed": 0,  # 0 for no multiple winners, 1 for allowing multiple winners in a round
        "variable_round_length": {
            "enabled": True,
            "min_rounds": 50,
            "max_rounds": 200
        },
        "move_outcomes": {
            "rock": {"scissors": 1, "rock": 0, "paper": -1},
            "paper": {"rock": 1, "paper": 0, "scissors": -1},
            "scissors": {"paper": 1, "scissors": 0, "rock": -1}
        }
    },
    "match": {
        "default_type": "round-robin",  # Default match type
        "types": {
            "round-robin": {
                "num_games_per_pair": 1  # Each pair of strategies plays 1 game by default
            },
            "single-elimination": {
                "advance_criteria": "winner"  # Winner advances to the next round
            },
            # Add other match types here if needed
    
        },
        "pairing": {
            "performance_based": 1,
            "adjustment_interval": 100
        }
    },
    "simulation": {
        "rounds": range(10, 1001, 10),  # range of rounds per simulation
        "match_type": "round-robin",  # Match type for all matches in this simulation
        "logging": {
            "log_filename": f"{result_file_path}/simulation_log.txt",
            "progress_interval": 10  # Percentage intervals for logging progress updates
        },
        "output": {
            "filename": f"{result_file_path}/simulation_results.csv",
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
    "history": {
        "limits": 10000000,
        "store_global_history": 0,
        "output": {
            "filename": f"{result_file_path}/history_global.csv",
            "columns": [
                "ID", "Move"
            ]
        }
    }
}
