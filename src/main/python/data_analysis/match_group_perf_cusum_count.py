import os
import pandas as pd
import numpy as np
import os

# Base directory for all data
base_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
data_file_path = f"{base_file_path}/data"
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = f"{base_file_path}/results"
cusum_results_file_path = f"{results_file_path}/cusum"

# Ensure the results directory exists
os.makedirs(cusum_results_file_path, exist_ok=True)

# Load data
data = pd.read_csv(f"{cusum_results_file_path}/match_group_perf_cusum.csv")

# Initialize structures to store results
stage_performance = []
category_counts = {strategy: {'Slightly Superior': 0, 'Gradually Superior': 0,
                              'Significantly Superior': 0, 'No Significant Difference': 0,
                              'Highly Fluctuating': 0} for strategy in pd.concat([data['strategy1_abbr'], data['strategy2_abbr']]).unique()}

# Function to categorize performance dynamically based on thresholds
def categorize_performance(mean, trend, std, thresholds):
    """Categorize performance using dynamic thresholds."""
    mean_threshold, trend_threshold, std_threshold = thresholds
    if abs(mean) < mean_threshold and std < std_threshold:
        return 'No Significant Difference'
    elif std > 2 * std_threshold:
        return 'Highly Fluctuating'
    elif mean > 2 * mean_threshold:
        return 'Significantly Superior'
    elif mean > mean_threshold and trend > trend_threshold:
        return 'Gradually Superior'
    elif mean > mean_threshold:
        return 'Slightly Superior'
    else:
        return 'No Significant Difference'

# Analyze each strategy pair
for (strategy1, strategy2), group in data.groupby(['strategy1_abbr', 'strategy2_abbr']):
    # Calculate dynamic thresholds based on each match pair's statistics
    wrd_range = group['sma_wrd'].max() - group['sma_wrd'].min()
    mean_threshold = wrd_range / 8  # Increase sensitivity
    std_threshold = group['sma_wrd'].std() / 2  # Reduce strictness
    trend_threshold = mean_threshold / 3  # Lower trend sensitivity
    thresholds = (mean_threshold, trend_threshold, std_threshold)

    # Define dynamic stages based on percentiles of 'rpg'
    rpg_values = group['rpg'].unique()
    quantiles = np.percentile(rpg_values, [0, 33, 67, 100])
    stages = {
        'early': (quantiles[0], quantiles[1]),
        'mid': (quantiles[1], quantiles[2]),
        'late': (quantiles[2], quantiles[3])
    }

    for stage_name, (start, end) in stages.items():
        # Filter data for the current stage
        stage_data = group[(group['rpg'] >= start) & (group['rpg'] <= end)]
        if stage_data.empty:
            continue
        
        # Calculate metrics for the stage based on `sma_wrd` (disparity in win rate)
        wrd_mean = stage_data['sma_wrd'].mean()
        wrd_trend = stage_data['sma_wrd'].iloc[-1] - stage_data['sma_wrd'].iloc[0] if len(stage_data) > 1 else 0
        wrd_std = stage_data['sma_wrd'].std()

        # Categorize and save stage performance based on dynamic thresholds
        category = categorize_performance(wrd_mean, wrd_trend, wrd_std, thresholds)
        stage_performance.append({
            'strategy1_abbr': strategy1,
            'strategy2_abbr': strategy2,
            'stage': stage_name,
            'category': category
        })

        # Increment count for each strategy's category
        category_counts[strategy1][category] += 1
        category_counts[strategy2][category] += 1

# Convert stage performance to DataFrame and save
stage_performance_df = pd.DataFrame(stage_performance)
output_file_stage_perf = f"{cusum_results_file_path}/match_group_perf_by_stage.csv"
stage_performance_df.to_csv(output_file_stage_perf, index=False)

# Convert category counts to DataFrame and save
category_counts_df = pd.DataFrame(category_counts).T.reset_index().rename(columns={'index': 'strategy_abbr'})
output_file_counts = f"{cusum_results_file_path}/match_group_perf_stage_summary.csv"
category_counts_df.to_csv(output_file_counts, index=False)

print(f"Stage performance saved to {output_file_stage_perf}")
print(f"Category counts saved to {output_file_counts}")
