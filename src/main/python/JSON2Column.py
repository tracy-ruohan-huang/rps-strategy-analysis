import pandas as pd
import json
import os
import datetime

def extract_columns_from_json(json_data):
    columns = []

    def recurse(data, parent_key=''):
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    recurse(value, new_key)
                elif isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        recurse(value[0], new_key)
                    else:
                        columns.append(new_key)
                else:
                    columns.append(new_key)
        else:
            columns.append(parent_key)
    
    recurse(json_data)
    print("Extracted columns:", columns)
    return columns

# Directory path
directory = 'BillboardExplain/data'

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Generate timestamp
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# Step 1: Read the CSV file containing all the flattened JSON data
csv_file_path = os.path.join(directory, 'spotify_billboard_hot_100_20240707_142446.csv')

try:
    df_all_data = pd.read_csv(csv_file_path, error_bad_lines=False)
except pd.errors.ParserError as e:
    print(f"ParserError: {e}")
    # Handle the error as needed, e.g., log it or exit gracefully

# Print DataFrame columns to inspect
print("Columns in the DataFrame:", df_all_data.columns.tolist())

# Step 2: Read the JSON file that contains the subset of JSON data type
json_file_path = os.path.join(directory, 'Spotify_Track_Part.json')

with open(json_file_path, 'r') as file:
    subset_data_type = json.load(file)

subset_columns = extract_columns_from_json(subset_data_type)

# Verify which columns from subset_columns exist in the DataFrame
existing_columns = [col for col in subset_columns if col in df_all_data.columns]

# Log the columns not found in the DataFrame
missing_columns = [col for col in subset_columns if col not in df_all_data.columns]
if missing_columns:
    print(f"The following columns were not found in the DataFrame: {missing_columns}")

# Step 3: Extract the subset of data from the CSV file based on the verified list of columns
df_subset = df_all_data[existing_columns]

# Step 4: Write the subset data to another CSV file
output_csv_file_path = os.path.join(directory, f'subset_data_{timestamp}.csv')
df_subset.to_csv(output_csv_file_path, index=False)

print(f"Subset data saved to {output_csv_file_path}")
