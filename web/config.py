import os
from pathlib import Path

# Base directory - two levels up from this file (web/config.py -> yolo-copy/)
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Flask application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # Paths
    SUSPICIOUS_EVENTS_DIR = BASE_DIR / 'suspicious_events'
    MAIN_SCRIPT_PATH = BASE_DIR / 'main.py'
    MODEL_PATH = BASE_DIR / 'best.pt'
    CONFIG_FILE = BASE_DIR / 'web' / 'system_config.json'
    
    # System defaults
    DEFAULT_RESOLUTION = '1640x1232'
    DEFAULT_THRESHOLD = 0.2
    DEFAULT_ANALYSIS_INTERVAL = 3
    
    # Server settings
    HOST = '0.0.0.0'  # Accessible on local network
    PORT = 5000
