import pandas as pd
import os

# Base directory for all data
base_file_path = 'rps_strategy_analysis'
data_file_path = f"{base_file_path}/data"
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = f"{base_file_path}/results"

# Ensure the results directory exists
os.makedirs(results_file_path, exist_ok=True)

# Load the strategy performance data
input_file_path = f"{processed_data_file_path}/strategy_perf.csv"  # Input file path
output_file_path = f"{results_file_path}/strategy_perf_ma.csv"  # Output file path
mean_output_file_path = f"{results_file_path}/strategy_perf_ma_summary.csv"  # Mean moving average output file

# Read the CSV file
strategy_perf = pd.read_csv(input_file_path)

# Debug: Check if data loaded correctly
print(f"Loaded {len(strategy_perf)} records from {input_file_path}")

# Calculate moving average for each strategy (grouped by strategy_abbr)
strategy_perf['ma_owr'] = (
    strategy_perf.groupby('strategy_abbr')['owr']
    .apply(lambda x: x.rolling(window=20, min_periods=1).mean())
    .reset_index(level=0, drop=True)  # Align indices to match the original DataFrame
)

# Format numbers to 2 decimal places for ma_owr
strategy_perf['ma_owr'] = strategy_perf['ma_owr'].round(2)

# Calculate the mean of the moving average (ma_owr) for each strategy
mean_ma_owr = strategy_perf.groupby('strategy_abbr')['ma_owr'].mean().reset_index()
mean_ma_owr.columns = ['strategy_abbr', 'mean_ma_owr']

# Format numbers to 2 decimal places for mean_ma_owr
mean_ma_owr['mean_ma_owr'] = mean_ma_owr['mean_ma_owr'].round(2)

# Save the mean moving average to a separate file
mean_ma_owr.to_csv(mean_output_file_path, index=False)

# Debug: Display a sample of the mean_ma_owr data
print("Mean Moving Average OWR:")
print(mean_ma_owr.head())

# Save the updated strategy performance data to a new file
strategy_perf.to_csv(output_file_path, index=False)

# Debug: Confirm completion
print(f"Moving average data saved to {output_file_path}")
print(f"Mean moving average saved to {mean_output_file_path}")
