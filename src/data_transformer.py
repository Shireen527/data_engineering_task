import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger
from config import Config

def transform_and_aggregate(df, file_name):
    logger.info(f"Starting transformation for {file_name}")
    if df.empty:
        logger.warning(f"Empty dataframe for {file_name}, no aggregation performed")
        return df, pd.DataFrame()

    df['file_source'] = file_name
      
    aggregates = []
    for metric in Config.SENSOR_METRICS:
        if metric in df.columns:
            agg_data = df.groupby(['machine_id'])[metric].agg(
                min_value='min',
                max_value='max', 
                avg_value='mean',
                std_dev='std',
                record_count='count'
            ).reset_index()
            
            agg_data['metric_name'] = metric
            agg_data['window_start'] = df['timestamp'].min()
            agg_data['window_end'] = df['timestamp'].max()
            agg_data['file_source'] = file_name
            agg_data['processed_at'] = datetime.now()
            
            aggregates.append(agg_data)
    

    if aggregates:
        aggregated_df = pd.concat(aggregates, ignore_index=True)
        logger.success(f"Transformation complete: {len(df)} rows → {len(aggregated_df)} aggregates")
    else:
        aggregated_df = pd.DataFrame()
        logger.warning(f"No aggregates generated for {file_name}")
     
    return df, aggregated_df
