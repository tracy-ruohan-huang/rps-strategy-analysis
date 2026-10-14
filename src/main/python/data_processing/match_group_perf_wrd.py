import os
import pandas as pd
import itertools
import os

# Base directory for all data
base_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
data_file_path = os.path.join(base_file_path, 'data')
processed_data_file_path = f"{data_file_path}/processed"

# Load processed match group performance data
match_group_perf_processed = pd.read_csv(f"{processed_data_file_path}/match_group_perf_processed.csv")

# Step 1: Calculate pairwise WRD for each match group based on pwr_mean
def calculate_pairwise_wrd(data):
    wrd_records = []
    for (mg_id, rpg), group in data.groupby(["mg_id", "rpg"]):
        # Generate all unique pairs of strategies within the same match group
        for (idx1, strat1), (idx2, strat2) in itertools.combinations(group.iterrows(), 2):
            # wrd = round(abs(strat1["pwr"] - strat2["pwr"]), 2)
            wrd = round(strat1["pwr"] - strat2["pwr"], 2)
            wrd_records.append({
                "mg_id": mg_id,
                "rpg": rpg,
                "strategy1_abbr": strat1["strategy_abbr"],
                "strategy2_abbr": strat2["strategy_abbr"],
                "pwr1": strat1["pwr"],
                "pwr2": strat2["pwr"],
                "wrd": wrd
            })
    return pd.DataFrame(wrd_records)

# Calculate WRD and save detailed WRD data
wrd_data = calculate_pairwise_wrd(match_group_perf_processed)
wrd_data.to_csv(f"{processed_data_file_path}/match_group_perf_wrd.csv", index=False)
print(f"WRD data saved to {processed_data_file_path}/match_group_perf_wrd.csv")

# Step 2: Aggregate WRD data by 'mg_id', 'strategy1_abbr', and 'strategy2_abbr'
# to calculate pwr1_mean, pwr1_std, pwr2_mean, pwr2_std, wrd_mean, and wrd_std
def aggregate_wrd_summary(wrd_data):
    summary = wrd_data.groupby(["mg_id", "strategy1_abbr", "strategy2_abbr"]).agg(
        pwr1_mean=('pwr1', 'mean'),
        pwr1_std=('pwr1', 'std'),
        pwr2_mean=('pwr2', 'mean'),
        pwr2_std=('pwr2', 'std'),
        wrd_mean=('wrd', 'mean'),
        wrd_std=('wrd', 'std')
    ).reset_index()
    
    # Round all numerical columns to two decimal places
    summary[['pwr1_mean', 'pwr1_std', 'pwr2_mean', 'pwr2_std', 'wrd_mean', 'wrd_std']] = summary[
        ['pwr1_mean', 'pwr1_std', 'pwr2_mean', 'pwr2_std', 'wrd_mean', 'wrd_std']
    ].round(2)
    
    return summary

# Calculate WRD summary and save to file
wrd_summary = aggregate_wrd_summary(wrd_data)
wrd_summary.to_csv(f"{processed_data_file_path}/match_group_perf_wrd_summary.csv", index=False)
print(f"WRD summary saved to {processed_data_file_path}/match_group_perf_wrd_summary.csv")
