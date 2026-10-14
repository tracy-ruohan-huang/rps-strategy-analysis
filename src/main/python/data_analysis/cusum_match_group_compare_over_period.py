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
wrd_data = pd.read_csv(f"{processed_data_file_path}/match_group_perf_wrd.csv")

# Define time periods
time_periods = {
    'Early': (10, 330),
    'Mid-term': (340, 670),
    'Late': (680, 1000)
}

# Dynamically get all unique match groups (strategy pairs)
all_groups = wrd_data[['strategy1_abbr', 'strategy2_abbr']].drop_duplicates()
all_groups = list(zip(all_groups['strategy1_abbr'], all_groups['strategy2_abbr']))

# Initialize an empty list to store the results
performance_table = []

# Function to calculate performance and fluctuation for each time period
def analyze_performance(data, strategy1, strategy2, period_range):
    period_data = data[(data['rpg'] >= period_range[0]) & (data['rpg'] <= period_range[1])]
    mean_pwr1 = period_data['pwr1'].mean()
    mean_pwr2 = period_data['pwr2'].mean()
    pwr_std1 = period_data['pwr1'].std()
    pwr_std2 = period_data['pwr2'].std()
    diff = mean_pwr2 - mean_pwr1

    if diff > 20:
        result = f"{strategy2} significantly superior"
    elif diff > 10:
        result = f"{strategy2} expands its advantage"
    elif diff > 5:
        result = f"{strategy2} gradually superior"
    elif diff > 0:
        result = f"{strategy2} slightly superior"
    elif diff < -20:
        result = f"{strategy1} significantly superior"
    elif diff < -10:
        result = f"{strategy1} expands its advantage"
    elif diff < -5:
        result = f"{strategy1} gradually superior"
    elif diff < 0:
        result = f"{strategy1} slightly superior"
    else:
        result = "Balanced"

    fluctuation = max(pwr_std1, pwr_std2)
    return result, round(diff, 2), round(fluctuation, 2)

# Analyze each match group and time period
for strategy1, strategy2 in all_groups:
    match_group_data = wrd_data[
        ((wrd_data['strategy1_abbr'] == strategy1) & (wrd_data['strategy2_abbr'] == strategy2)) |
        ((wrd_data['strategy1_abbr'] == strategy2) & (wrd_data['strategy2_abbr'] == strategy1))
    ].sort_values(by='rpg').reset_index(drop=True)

    # Store comparative performance and fluctuation for each period
    result_row = [f"({strategy1}, {strategy2})"]
    for period_name, period_range in time_periods.items():
        performance_description, diff, fluctuation = analyze_performance(match_group_data, strategy1, strategy2, period_range)
        result_row.extend([performance_description, f"{diff:.2f}", f"{fluctuation:.2f}"])

    performance_table.append(result_row)

# Convert results to DataFrame
columns = ["Match Group"]
for period in time_periods.keys():
    columns.extend([f"{period} Performance", f"{period} Diff", f"{period} Fluctuation"])

performance_df = pd.DataFrame(performance_table, columns=columns)

# Save to CSV
performance_df.to_csv(f"{cusum_results_file_path}/performance_comparison_table.csv", index=False)
print(performance_df)
