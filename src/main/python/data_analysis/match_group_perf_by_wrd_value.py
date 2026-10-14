import pandas as pd

# Base directory for all data
data_file_path = 'rps_strategy_analysis/data'
processed_data_file_path = f"{data_file_path}/processed"
results_file_path = 'rps_strategy_analysis/results'

# Load the dataset
data = pd.read_csv(f"{processed_data_file_path}/match_group_perf_summary_wrd.csv")

# Function to categorize WRD Mean
def categorize_wrd_mean(value):
    if value <= 5:
        return "Extremely Low"
    elif 5 < value <= 15:
        return "Low"
    elif 15 < value <= 40:
        return "Balanced"
    elif 40 < value <= 70:
        return "High"
    else:
        return "Extremely High"

# Function to categorize WRD Std Dev
def categorize_wrd_std(value):
    if value <= 2:
        return "Extremely Low"
    elif 2 < value <= 5:
        return "Low"
    elif 5 < value <= 10:
        return "Balanced"
    elif 10 < value <= 15:
        return "High"
    else:
        return "Extremely High"

# Refined function to determine the main 'category' based on WRD Mean and WRD Std
def refined_categorize(row):
    wrd_mean = row['wrd_mean']
    wrd_std = row['wrd_std']
    
    # Refined logic for categories
    if wrd_mean >= 60 and wrd_std <= 25:
        return 'Extreme Dominance (EH)'
    elif 40 <= wrd_mean < 60 and wrd_std > 5:
        return 'Consistent Advantage (H)'
    elif 10 <= wrd_mean < 40 and wrd_std <= 10:
        return 'Competitive Balance (B)'
    elif wrd_mean < 10 and wrd_std <= 10:
        return 'Marginal Superiority (EL)'
    else:
        return 'Competitive Balance (B)'

# Apply the categorization functions for WRD Mean and WRD Std
data['wrd_mean_category'] = data['wrd_mean'].apply(categorize_wrd_mean)
data['wrd_std_category'] = data['wrd_std'].apply(categorize_wrd_std)

# Apply the refined main categorization function for the overall 'category' column
data['category'] = data.apply(refined_categorize, axis=1)

# Save the output to a new CSV file in the current directory
output_path_refined = "match_group_perf_summary_with_refined_category.csv"
data.to_csv(output_path_refined, index=False)

# Display the first few rows for verification
print(data[['mg_id', 'strategy1_abbr', 'strategy2_abbr', 'wrd_mean', 'wrd_mean_category', 'wrd_std', 'wrd_std_category', 'category']].head())
