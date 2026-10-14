import pandas as pd

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = 'rps_strategy_analysis/results'

# Load the dataset
data = pd.read_csv(f"{processed_data_file_path}/match_group_perf_summary_wrd.csv")

# Calculate percentiles and mean, std for `wrd_mean` and `wrd_std`
wrd_mean_25 = data['wrd_mean'].quantile(0.25)
wrd_mean_75 = data['wrd_mean'].quantile(0.75)
wrd_mean_10 = data['wrd_mean'].quantile(0.10)
wrd_mean_90 = data['wrd_mean'].quantile(0.90)

wrd_std_25 = data['wrd_std'].quantile(0.25)
wrd_std_75 = data['wrd_std'].quantile(0.75)
wrd_std_10 = data['wrd_std'].quantile(0.10)
wrd_std_90 = data['wrd_std'].quantile(0.90)

# Define categories based on these thresholds
def categorize_wrd(row):
    if row['wrd_mean'] >= wrd_mean_90:
        return "Extreme High WRD"
    elif row['wrd_mean'] >= wrd_mean_75:
        return "High WRD"
    elif row['wrd_mean'] <= wrd_mean_10:
        return "Extreme Low WRD"
    elif row['wrd_mean'] <= wrd_mean_25:
        return "Low WRD"
    else:
        return "Balanced WRD"

def categorize_wrd_std(row):
    if row['wrd_std'] >= wrd_std_90:
        return "Extreme High WRD Std"
    elif row['wrd_std'] >= wrd_std_75:
        return "High WRD Std"
    elif row['wrd_std'] <= wrd_std_10:
        return "Extreme Low WRD Std"
    elif row['wrd_std'] <= wrd_std_25:
        return "Low WRD Std"
    else:
        return "Balanced WRD Std"

# Apply categorization
data['WRD_Category'] = data.apply(categorize_wrd, axis=1)
data['WRD_Std_Category'] = data.apply(categorize_wrd_std, axis=1)

# Save or display the categorized data
data.to_csv(f"{results_file_path}/match_group_perf_summary_by_wrd_percentile.csv", index=False)
print(data[['mg_id', 'WRD_Category', 'WRD_Std_Category']])
