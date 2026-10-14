import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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

# Dynamically get all unique match groups (strategy pairs)
all_groups = wrd_data[['strategy1_abbr', 'strategy2_abbr']].drop_duplicates()
all_groups = list(zip(all_groups['strategy1_abbr'], all_groups['strategy2_abbr']))

# CUSUM calculation function with a fixed baseline (pwr_mean)
def calculate_cusum(data, col_name, baseline):
    """Calculate CUSUM values for a specified column with a fixed baseline mean."""
    cusum_values = data[col_name] - baseline
    cusum = np.cumsum(cusum_values)
    return cusum

# Moving Average CUSUM calculation
def calculate_moving_average_cusum(cusum, window=20):
    """Calculate Moving Average of CUSUM for a specified window size."""
    return pd.Series(cusum).rolling(window=window, min_periods=1).mean()

# Create a PDF file to save all plots
pdf_path = f"{cusum_results_file_path}/match_group_cusum_plots_wrd_noabs.pdf"
with PdfPages(pdf_path) as pdf:
    for strategy1, strategy2 in all_groups:
        # Filter data for the specific match group
        match_group_data = wrd_data[
            ((wrd_data['strategy1_abbr'] == strategy1) & (wrd_data['strategy2_abbr'] == strategy2)) |
            ((wrd_data['strategy1_abbr'] == strategy2) & (wrd_data['strategy2_abbr'] == strategy1))
        ]
        
        # Ensure data is sorted by 'rpg' (rounds per game) for time-series analysis
        match_group_data = match_group_data.sort_values(by='rpg').reset_index(drop=True)
        
        # Set baseline using pwr_mean from the data
        baseline_s1 = match_group_data['pwr1'].mean()
        baseline_s2 = match_group_data['pwr2'].mean()
        baseline_wrd = match_group_data['wrd'].mean()
        
        # Calculate CUSUM and MA CUSUM for PWR of both strategies and WRD using pwr_mean as baseline
        cusum_s1 = calculate_cusum(match_group_data, 'pwr1', baseline_s1)
        ma_cusum_s1 = calculate_moving_average_cusum(cusum_s1)
        
        cusum_s2 = calculate_cusum(match_group_data, 'pwr2', baseline_s2)
        ma_cusum_s2 = calculate_moving_average_cusum(cusum_s2)
        
        cusum_wrd = calculate_cusum(match_group_data, 'wrd', baseline_wrd)
        ma_cusum_wrd = calculate_moving_average_cusum(cusum_wrd)
        
        # Calculate dynamic control limits using ±2 times the standard deviation of CUSUM values
        ucl_s1, lcl_s1 = 2 * cusum_s1.std(), -2 * cusum_s1.std()
        ucl_s2, lcl_s2 = 2 * cusum_s2.std(), -2 * cusum_s2.std()
        ucl_wrd, lcl_wrd = 2 * cusum_wrd.std(), -2 * cusum_wrd.std()

        # Plotting
        fig, axs = plt.subplots(1, 3, figsize=(21, 6))  # Adjusted layout for 3 subplots
        
        # Plot PWR for Strategy 1 and Strategy 2 (Comparative Performance)
        axs[0].plot(match_group_data['rpg'], match_group_data['pwr1'], label=f"{strategy1}", color="blue", linewidth=2)
        axs[0].plot(match_group_data['rpg'], match_group_data['pwr2'], label=f"{strategy2}", color="darkorange", linewidth=2)
        axs[0].set_title(f"Comparative Performance: {strategy1} vs {strategy2}")
        axs[0].set_xlabel("Rounds")
        axs[0].set_ylabel("Win Rate (%)")
        axs[0].legend()
        axs[0].grid()
        
        # Plot CUSUM for Strategy 1 and Strategy 2 with control limits for PWR
        axs[1].plot(match_group_data['rpg'], cusum_s1, label=f"{strategy1}", color="blue", linewidth=2)
        axs[1].plot(match_group_data['rpg'], cusum_s2, label=f"{strategy2}", color="darkorange", linewidth=2)
        axs[1].plot(match_group_data['rpg'], ma_cusum_s1, label="Moving Avg.", linestyle="--", color="blue", linewidth=1)
        axs[1].plot(match_group_data['rpg'], ma_cusum_s2, linestyle="--", color="darkorange")
        
        # Add control limits for both strategies
        axs[1].axhline(ucl_s1, color="blue", linestyle=":", linewidth=1, label=f"Ctrl. Limits")
        axs[1].axhline(lcl_s1, color="blue", linestyle=":", linewidth=1)
        axs[1].axhline(ucl_s2, color="darkorange", linestyle=":", linewidth=1)
        axs[1].axhline(lcl_s2, color="darkorange", linestyle=":")

        axs[1].set_title(f"Cumulative Strategy Performance: {strategy1} vs {strategy2}")
        axs[1].set_xlabel("Rounds")
        axs[1].set_ylabel("CUSUM")
        axs[1].legend()
        axs[1].grid()
        
        # Plot CUSUM and MA CUSUM for WRD with control limits
        axs[2].plot(match_group_data['rpg'], cusum_wrd, label="Disparity", color="green", linewidth=2)
        axs[2].plot(match_group_data['rpg'], ma_cusum_wrd, label="Moving Avg.", linestyle="--", color="green")
        axs[2].axhline(ucl_wrd, color="green", linestyle=":", linewidth=1, label="Ctrl. Limits")
        axs[2].axhline(lcl_wrd, color="green", linestyle=":", linewidth=1)
        
        axs[2].set_title(f"Cumulative Strategy Performance Disparity: {strategy1} vs {strategy2}")
        axs[2].set_xlabel("Rounds")
        axs[2].set_ylabel("CUSUM")
        axs[2].legend()
        axs[2].grid()
        
        # Save the current figure to the PDF
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)  # Close the plot to free memory

        print(f"Added CUSUM plot for {strategy1} vs {strategy2} in match group to the PDF.")

print(f"All CUSUM plots saved in {pdf_path}")
