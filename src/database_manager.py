import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from loguru import logger
from config import Config
import time
from functools import wraps
from datetime import datetime

def retry(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Final retry failed: {e}")
                        raise e
                    wait_time = 2 ** attempt
                    logger.warning(f"Retry {attempt + 1}/{max_retries} in {wait_time}s: {e}")
                    time.sleep(wait_time)
        return wrapper
    return decorator


class DatabaseManager:    

    RAW_TABLE = "raw_sensor_data"
    AGG_TABLE = "sensor_aggregates"

    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
    
    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
    
    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")

    @retry(max_retries=3)
    def insert_raw_data(self, df):
        if df.empty:
            logger.warning("No raw data to insert")
            return
            
        self.connect()

        columns = ['machine_id', 'timestamp','temperature', 
                   'humidity', 'pressure', 'vibration',
                   'energy_consumption', 'machine_status', 'anomaly_flag',
                   'predicted_remaining_life', 'file_source', 'ingested_at']
        
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df['ingested_at'] = datetime.now()
        tuples = [tuple(x) for x in df[columns].to_numpy()]

        query = f"""INSERT INTO {self.RAW_TABLE} ({', '.join(columns)}) VALUES %s"""
        try:    
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, tuples, page_size=1000)
                self.conn.commit()
                
            logger.success(f"Inserted {len(tuples)} raw sensor records")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to insert raw data: {e}")
            raise
    
    @retry(max_retries=3)
    def insert_aggregates(self, df):
        if df.empty:
            logger.warning("No aggregated data to insert")
            return
            
        self.connect()
        columns = ['machine_id', 'window_start', 'window_end',
                   'metric_name', 'min_value', 'max_value', 'avg_value',
                   'std_dev', 'record_count', 'file_source', 'processed_at']
        
        for col in columns:
            if col not in df.columns:
                df[col] = None

        tuples = [tuple(x) for x in df[columns].to_numpy()]
        query = f"""INSERT INTO {self.AGG_TABLE} ({', '.join(columns)}) VALUES %s"""
            
        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, tuples, page_size=1000)
                self.conn.commit()
                
            logger.success(f"Inserted {len(tuples)} aggregate records")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to insert aggregates: {e}")
            raise
    
    def health_check(self):
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


def get_db_config():
    return {
        'host': Config.HOST,
        'port': Config.PORT,
        'dbname': Config.DBNAME,
        'user': Config.USER,
        'password': Config.PASSWORD
    }

