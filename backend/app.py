from flask import Flask
from flask_cors import CORS
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_config
from controllers.share_controller import ShareController
from controllers.ai_controller import AIController

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("env_loaded")
except Exception:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pooling for MongoDB
from pymongo import MongoClient
client = MongoClient(maxPoolSize=10, waitQueueTimeoutMS=5000)

app = Flask(__name__)

# Configure CORS explicitly for frontend origin and API routes
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:37839"]}},
    methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Register controllers
ShareController.register(app)
AIController.register(app)

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(app.config.get('LOG_FILE', 'stockbuddy.log')),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting StockBuddy Backend...")
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )