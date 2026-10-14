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
wrd_data = pd.read_csv(f"{cusum_results_file_path}/match_group_perf_cusum.csv")

# Phase ranges
phases = {
    'early': (10, 330),
    'middle': (340, 670),
    'late': (680, 1000)
}

# Function to calculate MASI (rolling standard deviation mean)
def calculate_masi(data, column_name):
    """Calculate MASI as the mean of the rolling standard deviation."""
    # rolling_std = data[column_name].rolling(window=window, min_periods=1).std()
    return data[column_name].std()

# Initialize a list to store the results
masi_results = []

# Calculate MASI for each strategy pair and phase
for strategy1, strategy2 in wrd_data[['strategy1_abbr', 'strategy2_abbr']].drop_duplicates().itertuples(index=False):
    # Filter data for the specific match group
    match_group_data = wrd_data[
        ((wrd_data['strategy1_abbr'] == strategy1) & (wrd_data['strategy2_abbr'] == strategy2)) |
        ((wrd_data['strategy1_abbr'] == strategy2) & (wrd_data['strategy2_abbr'] == strategy1))
    ]
    
    # Iterate through each phase
    for phase, (start, end) in phases.items():
        phase_data = match_group_data[(match_group_data['rpg'] >= start) & (match_group_data['rpg'] <= end)]
        
        if not phase_data.empty:
            # Calculate MASI for the specified metrics
            masi_sma_pwr1 = calculate_masi(phase_data, 'sma_pwr1')
            masi_sma_pwr2 = calculate_masi(phase_data, 'sma_pwr2')
            masi_ma_cusum_s1 = calculate_masi(phase_data, 'ma_cusum_s1')
            masi_ma_cusum_s2 = calculate_masi(phase_data, 'ma_cusum_s2')
            masi_sma_wrd = calculate_masi(phase_data, 'sma_wrd')
            masi_ma_cusum_wrd = calculate_masi(phase_data, 'ma_cusum_wrd')
            
            # Append the results
            masi_results.append({
                'strategy1_abbr': strategy1,
                'strategy2_abbr': strategy2,
                'phase': phase,
                'masi_sma_pwr1': masi_sma_pwr1,
                'masi_sma_pwr2': masi_sma_pwr2,
                'masi_ma_cusum_s1': masi_ma_cusum_s1,
                'masi_ma_cusum_s2': masi_ma_cusum_s2,
                'masi_sma_wrd': masi_sma_wrd,
                'masi_ma_cusum_wrd': masi_ma_cusum_wrd
            })

# Convert results to a DataFrame
masi_results_df = pd.DataFrame(masi_results)

# Format all numeric columns to two decimal places
for col in masi_results_df.select_dtypes(include=['float']).columns:
    masi_results_df[col] = masi_results_df[col].map("{:.2f}".format)

# Save results to a CSV file
output_csv_path = f"{cusum_results_file_path}/match_pairs_masi_results.csv"
masi_results_df.to_csv(output_csv_path, index=False)

print(f"MASI results saved to {output_csv_path}")
