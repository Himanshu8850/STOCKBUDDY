from flask import Blueprint, jsonify, request
from services.gemini_service import GeminiService
import time
import logging

logger = logging.getLogger(__name__)

class AIController:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.blueprint = Blueprint('ai', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register AI prediction routes."""
        self.blueprint.add_url_rule('/api/ai-predictions', 'ai_predictions', self.ai_predictions, methods=['POST', 'OPTIONS'])
    
    def ai_predictions(self):
        """Get AI predictions for multiple stocks."""
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return ('', 204)
        
        data = request.get_json()
        stocks = data.get('stocks', [])
        
        if not stocks or not isinstance(stocks, list):
            return jsonify({'error': 'No stocks provided'}), 400
        
        # Process in batches of 2 symbols
        batch_size = 2
        results = {}
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            batch_result = self.gemini_service.get_predictions_batch(batch)
            results.update(batch_result)
            time.sleep(0.5)  # Small delay between batches
        
        return jsonify(results)
    
    @staticmethod
    def register(app):
        """Register the blueprint with the Flask app."""
        controller = AIController()
        app.register_blueprint(controller.blueprint)