import pandas as pd
import numpy as np
import os

# Base directory for all data
base_file_path = 'rps_strategy_analysis'
data_file_path = f"{base_file_path}/data"
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = f"{base_file_path}/results"
cusum_results_file_path = f"{results_file_path}/cusum"

# Ensure the results directory exists
os.makedirs(cusum_results_file_path, exist_ok=True)

# Load data
data = pd.read_csv(f"{cusum_results_file_path}/strategy_perf_cusum.csv")

# Phase ranges
phases = {
    'early': (10, 330),
    'middle': (340, 670),
    'late': (680, 1000)
}

# Function to calculate MASI
def calculate_masi(data, column_name):
    """Calculate MASI as the standard deviation of the column values."""
    return data[column_name].std()

# Initialize a list to store the results
masi_results = []

# Calculate MASI for each strategy and phase
for strategy in data['strategy_abbr'].drop_duplicates():
    # Filter data for the specific strategy
    strategy_data = data[data['strategy_abbr'] == strategy]
    
    # Iterate through each phase
    for phase, (start, end) in phases.items():
        # Filter data for the current phase
        phase_data = strategy_data[(strategy_data['rpg'] >= start) & (strategy_data['rpg'] <= end)]
        
        if not phase_data.empty:
            # Calculate MASI for the specified metrics
            masi_sma_owr = calculate_masi(phase_data, 'sma_owr')
            masi_ma_cusum = calculate_masi(phase_data, 'moving_avg_cusum')
            
            # Append the results
            masi_results.append({
                'strategy_abbr': strategy,
                'phase': phase,
                'masi_sma_owr': masi_sma_owr,
                'masi_ma_cusum': masi_ma_cusum
            })

# Convert results to a DataFrame
masi_results_df = pd.DataFrame(masi_results)

# Format all numeric columns to two decimal places
for col in masi_results_df.select_dtypes(include=['float']).columns:
    masi_results_df[col] = masi_results_df[col].map("{:.2f}".format)

# Save results to a CSV file
output_csv_path = f"{cusum_results_file_path}/strategy_masi_results.csv"
masi_results_df.to_csv(output_csv_path, index=False)

print(f"MASI results saved to {output_csv_path}")
