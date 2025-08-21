from loguru import logger
import pandas as pd
import os
from src.config import Config

def validate_file(file_path):
    df = pd.read_csv(file_path)
    file_name = os.path.basename(file_path)

    missing_cols = [c for c in Config.REQUIRED_FIELDS if c not in df.columns]
    if missing_cols:
        os.makedirs(Config.QUARANTINE_FOLDER, exist_ok=True)
        quarantine_file = os.path.join(Config.QUARANTINE_FOLDER, f"quarantine_{file_name}")
        df.to_csv(quarantine_file, index=False)
        logger.error(f"{file_name}: missing required columns: {missing_cols}. Quarantined entire file: {quarantine_file}")
        return pd.DataFrame()

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    numeric_cols = [
    'temperature', 'humidity', 'pressure', 
    'vibration', 'energy_consumption',
    'predicted_remaining_life', 'machine_status']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Explicit business rule: missing anomaly_flag = 0 (no anomaly), missing machine_status = -1 (Unknown)
    if 'anomaly_flag' not in df.columns:
        df['anomaly_flag'] = 0
    else:
        df['anomaly_flag'] = pd.to_numeric(df['anomaly_flag'], errors='coerce').fillna(0).astype(int)

    if 'machine_status' not in df.columns:
        df['machine_status'] = -1
    else:
        df['machine_status'] = pd.to_numeric(df['machine_status'], errors='coerce').fillna(-1).astype(int)
 

    null_mask = df[Config.REQUIRED_FIELDS].isnull().any(axis=1)
    null_mask_copy = null_mask.copy()
    duplicate_mask = df.duplicated(subset=['machine_id', 'timestamp'], keep='first')
    
    # Range checks
    temp_invalid = ~df['temperature'].between(Config.TEMP_MIN, Config.TEMP_MAX)
    humidity_invalid = ~df['humidity'].between(Config.HUMIDITY_MIN, Config.HUMIDITY_MAX) 
    pressure_invalid = ~df['pressure'].between(Config.PRESSURE_MIN, Config.PRESSURE_MAX)
    vibration_invalid = ~df['vibration'].between(Config.VIBRATION_MIN, Config.VIBRATION_MAX)
    energy_consumption_invalid = ~df['energy_consumption'].between(Config.ENERGY_MIN, Config.ENERGY_MAX)
    timestamp_invalid = df['timestamp'].isnull()

    invalid_mask = null_mask | duplicate_mask | temp_invalid | humidity_invalid | pressure_invalid | timestamp_invalid | vibration_invalid | energy_consumption_invalid
    
    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    
    # Quarantine invalid data
    if not invalid_df.empty:
        os.makedirs(Config.QUARANTINE_FOLDER, exist_ok=True)
        quarantine_file = os.path.join(Config.QUARANTINE_FOLDER, f"quarantine_{file_name}")
        invalid_df.to_csv(quarantine_file, index=False)

        error_counts = {
            "missing_required": int(null_mask_copy.sum()),
            "temp_out_of_range": int(temp_invalid.sum()),
            "humidity_out_of_range": int(humidity_invalid.sum()),
            "pressure_out_of_range": int(pressure_invalid.sum()),
            "invalid_timestamp": int(timestamp_invalid.sum()),
            "duplicates": int(duplicate_mask.sum())
        }
        
        summary = "; ".join([f"{k}={v}" for k, v in error_counts.items() if v > 0])
        logger.warning(f"{file_name}: {len(invalid_df)} invalid rows | {summary}")
        logger.warning(f"Quarantined {len(invalid_df)} rows to {quarantine_file}")
    
    logger.success(f"Validation complete: {len(valid_df)} valid, {len(invalid_df)} invalid rows")
    return valid_df


