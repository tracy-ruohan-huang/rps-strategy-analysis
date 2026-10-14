import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
import os

# Base directory for all data
base_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
results_file_path = f"{base_file_path}/results"
cusum_results_file_path = f"{results_file_path}/cusum"
decay_results_file_path = f"{results_file_path}/expdec"

# Load data from the CSV file
data = pd.read_csv(f"{cusum_results_file_path}/match_group_perf_wrd_cusum.csv")

# Ensure the decay results directory exists
os.makedirs(decay_results_file_path, exist_ok=True)

# Output file for adaptability index and decay rate
output_csv_path = f"{decay_results_file_path}/match_group_decay_results.csv"
output_pdf_path = f"{decay_results_file_path}/match_group_decay_plots.pdf"

# Initialize a list to store results
results = []

# Define decay-weighted calculation and exponential model
def exponential_decay(data, decay_factor=0.05):
    """Apply exponential decay to each point as a weighted moving average."""
    decay_weights = np.exp(-decay_factor * np.arange(len(data)))
    decay_weights /= decay_weights.sum()  # Normalize weights
    return np.array([np.dot(data[:i+1][::-1], decay_weights[:i+1]) for i in range(len(data))])

def exponential_model(t, Y0, lam):
    """Exponential decay model for curve fitting."""
    return Y0 * np.exp(-lam * t)

def calculate_adaptability_index(decay_weighted_cusum):
    """Calculate the adaptability index as the average of absolute changes in decay-weighted CUSUM."""
    diff_cusum = np.diff(decay_weighted_cusum)
    return np.mean(np.abs(diff_cusum))

# Prepare PDF file for all plots
with PdfPages(output_pdf_path) as pdf:
    # Get unique match groups
    match_groups = data[['strategy1_abbr', 'strategy2_abbr']].drop_duplicates()
    
    for _, row in match_groups.iterrows():
        strategy1 = row['strategy1_abbr']
        strategy2 = row['strategy2_abbr']
        
        # Filter data for the specific match group
        match_group_data = data[
            ((data['strategy1_abbr'] == strategy1) & (data['strategy2_abbr'] == strategy2)) |
            ((data['strategy1_abbr'] == strategy2) & (data['strategy2_abbr'] == strategy1))
        ].sort_values(by='rpg').reset_index(drop=True)

        # Extract PWR and CUSUM data for both strategies
        pwr1 = match_group_data['pwr1'].values
        pwr2 = match_group_data['pwr2'].values
        cusum_s1 = match_group_data['cusum_s1'].values
        cusum_s2 = match_group_data['cusum_s2'].values
        rpg_data = match_group_data['rpg'].values
        
        # Calculate decay-weighted PWR for both strategies
        decay_factor = 0.05
        decay_weighted_pwr1 = exponential_decay(pwr1, decay_factor=decay_factor)
        decay_weighted_pwr2 = exponential_decay(pwr2, decay_factor=decay_factor)
        
        # Fit exponential decay model to decay-weighted PWR for each strategy
        time_data = np.arange(len(decay_weighted_pwr1))
        popt1, _ = curve_fit(exponential_model, time_data, decay_weighted_pwr1, maxfev=10000)
        Y0_fitted_s1, lambda_fitted_s1 = popt1
        fitted_decay_curve_s1 = exponential_model(time_data, Y0_fitted_s1, lambda_fitted_s1)
        
        popt2, _ = curve_fit(exponential_model, time_data, decay_weighted_pwr2, maxfev=10000)
        Y0_fitted_s2, lambda_fitted_s2 = popt2
        fitted_decay_curve_s2 = exponential_model(time_data, Y0_fitted_s2, lambda_fitted_s2)

        # Calculate decay-weighted CUSUM and adaptability index for both strategies
        decay_weighted_cusum_s1 = exponential_decay(cusum_s1, decay_factor=decay_factor)
        decay_weighted_cusum_s2 = exponential_decay(cusum_s2, decay_factor=decay_factor)
        adaptability_index_s1 = calculate_adaptability_index(decay_weighted_cusum_s1)
        adaptability_index_s2 = calculate_adaptability_index(decay_weighted_cusum_s2)

        # Append results to the list
        results.append({
            'strategy1_abbr': strategy1,
            'strategy2_abbr': strategy2,
            's1_adaptability_index': round(adaptability_index_s1, 2),
            's2_adaptability_index': round(adaptability_index_s2, 2),
            's1_decay_rate': round(lambda_fitted_s1, 4),
            's2_decay_rate': round(lambda_fitted_s2, 4)
        })

        # Plotting
        fig, axs = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot raw PWR, decay-weighted PWR, and fitted decay curve for both strategies
        axs[0].plot(rpg_data, pwr1, label=f"{strategy1} I-WR", color="blue", linewidth=0.8, alpha=0.7)
        axs[0].plot(rpg_data, decay_weighted_pwr1, label=f"{strategy1} D-WR", color="blue", linestyle="--", linewidth=1.5)
        axs[0].plot(rpg_data, fitted_decay_curve_s1, label=f"{strategy1} FDC (λ={lambda_fitted_s1:.4f})", color="blue", linestyle="-", linewidth=1)
        
        axs[0].plot(rpg_data, pwr2, label=f"{strategy2} I-WR", color="orange", linewidth=0.8, alpha=0.7)
        axs[0].plot(rpg_data, decay_weighted_pwr2, label=f"{strategy2} D-WR", color="orange", linestyle="--", linewidth=1.5)
        axs[0].plot(rpg_data, fitted_decay_curve_s2, label=f"{strategy2} FDC (λ={lambda_fitted_s2:.4f})", color="orange", linestyle="-", linewidth=1)

        axs[0].set_title(f"Decay-Weighted Win Rate Trend for {strategy1} vs {strategy2}")
        axs[0].set_xlabel("Rounds")
        axs[0].set_ylabel("Win Rate (%)")
        axs[0].legend(fontsize=9)
        axs[0].grid(True, linestyle=":", linewidth=0.5)
        
        # Plot CUSUM and Decay-Weighted CUSUM for both strategies, with AI in the label
        axs[1].plot(rpg_data, cusum_s1, label=f"{strategy1} CUSUM", color="blue", linewidth=0.8, alpha=0.7)
        axs[1].plot(rpg_data, cusum_s2, label=f"{strategy2}", color="orange", linewidth=0.8, alpha=0.7)
        axs[1].plot(rpg_data, decay_weighted_cusum_s1, label=f"{strategy1} D-CUSUM (AI={adaptability_index_s1:.2f})", color="blue", linestyle="--", linewidth=1.5)
        axs[1].plot(rpg_data, decay_weighted_cusum_s2, label=f"{strategy2} (AI={adaptability_index_s2:.2f})", color="orange", linestyle="--", linewidth=1.5)
        
        axs[1].set_title(f"Decay-Weighted CUSUM and Adaptability for {strategy1} vs {strategy2}")
        axs[1].set_xlabel("Rounds")
        axs[1].set_ylabel("CUSUM")
        axs[1].legend(fontsize=9)
        axs[1].grid(True, linestyle=":", linewidth=0.5)
        
        # Save the plot to the PDF
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        print(f"Added refined decay-weighted analysis plot with AI in label for match group: {strategy1} vs {strategy2}")

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(output_csv_path, index=False)

print(f"All refined decay-weighted analysis plots saved in {output_pdf_path}")
print(f"Adaptability Index and decay rates saved in {output_csv_path}")
