import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = 'rps_strategy_analysis/results'

# Load WRD summary data
wrd_summary_data = pd.read_csv(f"{processed_data_file_path}/match_group_perf_wrd_summary.csv")

# Step 1: Prepare WRD_MEAN Matrix
wrd_mean_data = wrd_summary_data.pivot(index='strategy1_abbr', columns='strategy2_abbr', values='wrd_mean')
wrd_mean_data = np.abs(wrd_mean_data)  # Take absolute values
wrd_mean_matrix = wrd_mean_data.combine_first(wrd_mean_data.T)  # Make it symmetric

# Step 2: Prepare WRD_STD Matrix
wrd_std_data = wrd_summary_data.pivot(index='strategy1_abbr', columns='strategy2_abbr', values='wrd_std')
wrd_std_matrix = wrd_std_data.combine_first(wrd_std_data.T)  # Make it symmetric

# Step 3: Mask lower triangle for WRD_STD and upper triangle for WRD_MEAN
mask_wrd_std = np.tril(np.ones(wrd_std_matrix.shape), k=-1).astype(bool)  # Mask lower triangle for WRD_STD
mask_wrd_mean = np.triu(np.ones(wrd_mean_matrix.shape), k=1).astype(bool)  # Mask upper triangle for WRD_MEAN

# Plotting
plt.figure(figsize=(12, 10))

# Plot WRD_STD in lower triangle with color bar on the right
ax = sns.heatmap(wrd_std_matrix, annot=True, mask=mask_wrd_std, cmap='YlGnBu', fmt=".2f", 
                 cbar=True, cbar_kws={'label': 'WRD_STD', 'orientation': 'vertical', 'location': 'right'}, vmin=wrd_std_matrix.min().min(), vmax=wrd_std_matrix.max().max())

# Plot WRD_MEAN in upper triangle with color bar on the left
sns.heatmap(wrd_mean_matrix, annot=True, mask=mask_wrd_mean, cmap='coolwarm', fmt=".2f", 
            cbar=True, cbar_kws={'label': 'WRD_MEAN', 'orientation': 'vertical', 'location': 'left'}, vmin=wrd_mean_matrix.min().min(), vmax=wrd_mean_matrix.max().max(), ax=ax)

# Adjust color bar labels and positions
cbar1 = ax.collections[0].colorbar
cbar1.set_label('WRD Std.', rotation=270, labelpad=15)
cbar1.ax.yaxis.set_ticks_position('right')

cbar2 = ax.collections[1].colorbar
cbar2.set_label('WRD Mean', rotation=90, labelpad=15)
cbar2.ax.yaxis.set_ticks_position('left')

plt.title('Heatmap of Absolute WRD Mean and Variance Across Match Pairs')
plt.xlabel('Strategy')
plt.ylabel('Strategy')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save the refined plot to a file
output_file = f"{results_file_path}/heatmap/match_group_perf_wrd_hm.png"
plt.savefig(output_file, dpi=300)  # Save at 300 DPI for higher quality
plt.show()

print(f"Exchanged heatmap saved to {output_file}")
