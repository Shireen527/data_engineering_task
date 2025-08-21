import os
import pandas as pd
import numpy as np
from src.config import Config
import sys

def introduce_missing_values(df, missing_rate=0.02, seed=42):
    np.random.seed(seed)
    df_copy = df.copy()

    allowed_missing = [
        "machine_id",
        "temperature",
        "vibration",
        "humidity",
        "pressure",
        "failure_type"
    ]

    numeric_cols = [col for col in allowed_missing if col in df_copy.columns]

    total_cells = df_copy[numeric_cols].size
    n_missing = int(total_cells * missing_rate)

    row_indices = np.random.randint(0, df_copy.shape[0], n_missing)
    col_indices = np.random.choice(len(numeric_cols), n_missing)

    for r, c in zip(row_indices, col_indices):
        df_copy.at[r, numeric_cols[c]] = np.nan

    return df_copy



def split_csv(input_file, output_folder=Config.DATA_FOLDER, split_minutes=Config.SPLIT_MINUTES):
    os.makedirs(output_folder, exist_ok=True)
    
    df = pd.read_csv(input_file, parse_dates=['timestamp'])
    df = introduce_missing_values(df, missing_rate=0.02)
    df = df.sort_values('timestamp')
    
    def round_down_time(dt):
        total_minutes = dt.timestamp() // 60
        rounded_minutes = (total_minutes // split_minutes) * split_minutes
        return pd.to_datetime(rounded_minutes * 60, unit='s')
    
    df['group'] = df['timestamp'].apply(round_down_time)
    

    for group_time, group_df in df.groupby('group'):
        filename = f"sensor_{group_time.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_folder, filename)
        
        group_df.drop(columns=['group']).to_csv(filepath, index=False)
        print(f"Created {filename} , {len(group_df)} rows")

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "archive/smart_manufacturing_data.csv"
    split_csv(input_path)
