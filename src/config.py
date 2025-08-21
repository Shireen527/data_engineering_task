from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    HOST = os.getenv('DB_HOST')
    PORT = int(os.getenv('DB_PORT'))
    DBNAME = os.getenv('DB_NAME')
    USER = os.getenv('DB_USER')
    PASSWORD = os.getenv('DB_PASSWORD')
    DATA_FOLDER = './data'
    QUARANTINE_FOLDER = './quarantine'
    LOG_FILE = os.path.join('./logs', "pipeline.log")
    SPLIT_MINUTES = 800
    MONITORING_INTERVAL = 5

    # Validation rules
    TEMP_MIN = 20
    TEMP_MAX = 125
    HUMIDITY_MIN = 20
    HUMIDITY_MAX = 80
    PRESSURE_MIN = 0.5
    PRESSURE_MAX = 6
    VIBRATION_MIN = -17
    VIBRATION_MAX = 115
    ENERGY_MIN = 0.5
    ENERGY_MAX = 6
    
    REQUIRED_FIELDS = ['machine_id', 'timestamp', 'temperature', 'humidity', 'pressure', 'vibration', 'energy_consumption']
    SENSOR_METRICS = ['temperature', 'humidity', 'pressure', 'vibration', 'energy_consumption']



