"""
Configuration settings for StockBuddy Backend
"""
import os
from urllib.parse import quote_plus

class Config:
    """Base configuration"""
    
    # Flask Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Database Configuration
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'text')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '123')
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'cluster0.stfphmt.mongodb.net')
    MONGODB_DB = os.getenv('MONGODB_DB', 'Shares')
    
    # Construct MongoDB URI with proper encoding
    MONGODB_URI = f'mongodb+srv://{quote_plus(MONGODB_USERNAME)}:{quote_plus(MONGODB_PASSWORD)}@{MONGODB_HOST}/'
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))  # seconds
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))  # seconds
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per hour')
    
    # External API URLs
    GROWW_SEARCH_URL = 'https://groww.in/v1/api/search/v3/query/global/st_p_query'
    GROWW_PRICE_URL = 'https://groww.in/v1/api/stocks_data/v1/tr_live_prices/exchange/NSE/segment/CASH'
    GROWW_CHART_URL = 'https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH'
    
    # ML Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', '12_12min(pro3).keras')
    FEATURE_CACHE_SIZE = int(os.getenv('FEATURE_CACHE_SIZE', '128'))
    
    # Selenium Configuration
    WEBDRIVER_TIMEOUT = int(os.getenv('WEBDRIVER_TIMEOUT', '30'))
    BROWSER_PATH = os.getenv('BROWSER_PATH', '/usr/bin/brave-browser')
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'stockbuddy.log')
    
    # Performance Settings
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    CONNECTION_POOL_SIZE = int(os.getenv('CONNECTION_POOL_SIZE', '10'))
    WAIT_QUEUE_TIMEOUT = int(os.getenv('WAIT_QUEUE_TIMEOUT', '5000'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_DB = 'test_shares'

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
