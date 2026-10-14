import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations_with_replacement
from matplotlib.backends.backend_pdf import PdfPages
import os

data_dir = 'WinRPS\data'
csv_file_name = 'strategy_simulation_results.csv'
pdf_file_name = 'strategy_cusum_plots.pdf'
png_file_name = 'strategy_cusum_plots.png'
    
# Ensure output directory exists
os.makedirs(data_dir, exist_ok=True)

# Save results to CSV
input_csv_file = os.path.join(data_dir, csv_file_name)
output_pdf_file = os.path.join(data_dir, pdf_file_name)
output_png_file = os.path.join(data_dir, png_file_name)
# Load the data
data = pd.read_csv(input_csv_file)

# Simplified strategy names
strategy_names = [
    "Random",
    "Constant",
    "Sequential",
    "Mirror",
    "Exclusion",
    "Reaction",
    "ReverseMirror",
    "ProbWeighted",
    "MultiRoundObs"
]

# Function to generate combinations of strategies
def generate_combinations(strategy_list):
    return list(combinations_with_replacement(strategy_list, 2))

# Generate combinations of strategies
combinations = generate_combinations(strategy_names)

# Function to compute CUSUM
def compute_cusum(series, target_mean):
    return (series - target_mean).cumsum()

# Set up the plot grid
n_combinations = len(combinations)
n_rows = 10  # Fixed number of rows
n_cols = (n_combinations + n_rows - 1) // n_rows  # Calculate the number of columns needed

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 5))
axes = axes.flatten()  # Flatten the 2D array of axes to 1D for easy iteration

# Save all plots to a single PDF file
with PdfPages(output_pdf_file) as pdf:
    for idx, (strat1, strat2) in enumerate(combinations):
        # Filter data for the current strategy combination
        subset = data[(data['S1'] == strat1) & (data['S2'] == strat2)]
        if not subset.empty:
            # Compute CUSUM for 'Win Rate Difference' (or any other metric)
            target_mean = subset['%WDif'].mean()
            cusum = compute_cusum(subset['%WDif'], target_mean)

            # Plot
            ax = axes[idx]
            ax.plot(subset['Rnd'], cusum, marker='o', linestyle='-')
            ax.set_title(f'{strat1} vs {strat2}')
            ax.set_xlabel('Rounds')
            ax.set_ylabel('CUSUM')
            ax.grid(True)

            # Create a separate figure for the PDF
            plt.figure(figsize=(10, 6))
            plt.plot(subset['Rnd'], cusum, marker='o', linestyle='-')
            plt.title(f'{strat1} vs {strat2}')
            plt.xlabel('Rounds')
            plt.ylabel('CUSUM')
            plt.grid(True)

            # Save the current plot to the PDF
            pdf.savefig()
            plt.close()
        else:
            # If no data for the combination, hide the subplot
            axes[idx].axis('off')

# Hide any remaining empty plots
for idx in range(len(combinations), len(axes)):
    axes[idx].axis('off')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig(output_png_file)
plt.show()

print(f'All plots have been saved to {pdf_file_name} and {png_file_name}')
