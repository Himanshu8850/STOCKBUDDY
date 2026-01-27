from flask import Flask, send_from_directory
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

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../build"),
    static_url_path="",
)

# Configure CORS explicitly for frontend origin and API routes
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:37839",
    os.getenv("FRONTEND_URL", "*")  # Production URL from environment
]
CORS(
    app,
    resources={r"/*": {"origins": allowed_origins}},
    methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Register controllers
ShareController.register(app)
AIController.register(app)


# Serve React build assets
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    # Serve API routes first (they're registered above)
    if path.startswith("api/") or path.startswith("shares"):
        return app.send_static_file("index.html")  # This won't execute; API routes handled above
    
    # Check if file exists in build folder
    if path and os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # For all other routes, serve index.html (SPA routing)
    return send_from_directory(app.static_folder, "index.html")

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