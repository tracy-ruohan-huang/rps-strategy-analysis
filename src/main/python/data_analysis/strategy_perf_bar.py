import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = 'rps_strategy_analysis/results'

# Load the strategy performance summary data
strategy_perf_summary = pd.read_csv(f"{processed_data_file_path}/strategy_perf_summary.csv")

# Sort the data by 'owr_mean' for better visualization in the bar chart
strategy_perf_summary = strategy_perf_summary.sort_values(by='owr_mean', ascending=False)

# Set up the x locations for the groups and bar width
x = np.arange(len(strategy_perf_summary['strategy_abbr']))  # the label locations
bar_width = 0.5  # width of the bars

# Plot the bar chart for 'owr_mean' with error bars for 'owr_std'
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x, strategy_perf_summary['owr_mean'], bar_width, yerr=strategy_perf_summary['owr_std'],
       label='OWR Mean ± Std Dev', color='skyblue', capsize=5)

# Add labels, title, and custom x-axis tick labels, etc.
ax.set_xlabel('Strategy')
ax.set_ylabel('OWR (%)')
ax.set_title('Comparison of OWR Mean with Standard Deviation by Strategy')
ax.set_xticks(x)
ax.set_xticklabels(strategy_perf_summary['strategy_abbr'], rotation=45, ha='right')
ax.legend()

plt.tight_layout()

# Save the bar chart to a file
output_file = f"{results_file_path}/strategy_perf_summary_bar_no_text.png"
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")
