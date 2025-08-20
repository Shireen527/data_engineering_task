import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from data_validator import validate_file
from data_transformer import transform_and_aggregate
from database_manager import DatabaseManager, get_db_config
from config import Config
from loguru import logger

logger.add(Config.LOG_FILE, rotation="10 MB", retention="5 days", compression="zip")

class CSVFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"New file detected: {event.src_path}")
            self.process_file(event.src_path)
    
    def process_file(self, file_path):
        try:
            logger.info(f"Processing {os.path.basename(file_path)}...")
            #pipeline
            valid_df = validate_file(file_path)
            transformed_df, aggregated_df = transform_and_aggregate(valid_df, file_path) 
            
            db = DatabaseManager(get_db_config())
            try:
                db.insert_raw_data(transformed_df)
                db.insert_aggregates(aggregated_df)
            finally:
                db.close()
            
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

class FileWatcher:
    def __init__(self, watch_folder=Config.DATA_FOLDER):
        self.watch_folder = watch_folder
        self.observer = Observer()
        os.makedirs(watch_folder, exist_ok=True)
    
    def start_monitoring(self):
        event_handler = CSVFileHandler()
        self.observer.schedule(event_handler, self.watch_folder, recursive=False)
        self.observer.start()
        
        logger.info(f"Monitoring started...")
        
        try:
            while True:
                time.sleep(Config.MONITORING_INTERVAL)
        except KeyboardInterrupt:
            self.observer.stop()
        
        self.observer.join()

if __name__ == "__main__":
    watcher = FileWatcher()
    watcher.start_monitoring()
