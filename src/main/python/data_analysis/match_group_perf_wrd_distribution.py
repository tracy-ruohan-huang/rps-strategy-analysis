import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = 'rps_strategy_analysis/results'

# Load the dataset
data = pd.read_csv(f"{processed_data_file_path}/match_group_perf_wrd_summary.csv")

# Initialize the plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot the distribution of wrd_mean
sns.histplot(abs(data['wrd_mean']), kde=True, ax=axes[0], color='skyblue', bins=20)
axes[0].set_title("Distribution of WRD Mean")
axes[0].set_xlabel("WRD Mean")
axes[0].set_ylabel("Frequency")

# Plot the distribution of wrd_std
sns.histplot(data['wrd_std'], kde=True, ax=axes[1], color='salmon', bins=20)
axes[1].set_title("Distribution of WRD Std Dev")
axes[1].set_xlabel("WRD Std Dev")
axes[1].set_ylabel("Frequency")

# Save the plots to a file
plt.tight_layout()
plt.savefig(f"{results_file_path}/wrd_distributions.png", dpi=300)  # Save at 300 DPI for higher quality

# Display the plots
plt.show()

