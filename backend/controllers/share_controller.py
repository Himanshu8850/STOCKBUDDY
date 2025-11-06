# controllers/share_controller.py
from flask import Blueprint, jsonify, request
from functools import wraps
from services.stock_service import StockService
from services.external_api_service import ExternalAPIService
from utils import validate_symbol, validate_numeric
import logging

logger = logging.getLogger(__name__)

class ShareController:
    def __init__(self):
        self.stock_service = StockService()
        self.api_service = ExternalAPIService()
        self.blueprint = Blueprint('share', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for share, search, and profit operations."""
        
        # Share routes
        self.blueprint.add_url_rule('/buy', 'buy_share', self.buy_share, methods=['POST'])
        self.blueprint.add_url_rule('/api/sell', 'sell_share', self.sell_share, methods=['DELETE'])
        self.blueprint.add_url_rule('/shares', 'get_shares', self.get_shares, methods=['GET'])
        
        # Search routes
        self.blueprint.add_url_rule('/api/searching', 'search_stock', self.search_stock, methods=['GET'])
        self.blueprint.add_url_rule('/api/new-search', 'new_search', self.new_search, methods=['GET'])
        
        # Chart/data routes
        self.blueprint.add_url_rule('/api/old-data', 'get_chart_data', self.get_chart_data, methods=['GET'])
        self.blueprint.add_url_rule('/api/live', 'get_live_data', self.get_live_data, methods=['GET'])
        
        # Profit routes
        self.blueprint.add_url_rule('/api/profit', 'get_profit', self.get_profit, methods=['GET'])
        
        # Health check
        self.blueprint.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
    
    def handle_api_errors(self, f):
        """Decorator to handle API errors."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Unexpected error in {f.__name__}: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        return decorated_function
    
    def buy_share(self):
        """Buy a share endpoint."""
        data = request.get_json()
        
        if not data or not all(key in data for key in ['symbol', 'price', 'qtx']):
            return jsonify({'error': 'Missing required fields: symbol, price, qtx'}), 400
        
        try:
            symbol = data['symbol'].strip().upper()
            price = float(data['price'])
            quantity = int(data['qtx'])
            
            if price <= 0 or quantity <= 0:
                return jsonify({'error': 'Price and quantity must be positive'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid price or quantity format'}), 400
        
        # Get scrip code from symbol
        scrip_code = self.api_service.search_stock(symbol)
        if not scrip_code:
            return jsonify({'error': 'Unable to validate symbol'}), 400
        
        # Buy share using service
        result = self.stock_service.buy_share(scrip_code, price, quantity)
        
        if result['success']:
            return jsonify({'message': result['message']})
        else:
            return jsonify({'error': result['error']}), 500
    
    def sell_share(self):
        """Sell a share endpoint."""
        symbol = request.args.get('symbol')
        profit_str = request.args.get('profit')
        
        if not symbol or profit_str is None:
            return jsonify({'error': 'Missing required parameters: symbol, profit'}), 400
        
        try:
            profit = float(profit_str)
            symbol = symbol.strip().upper()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid profit value'}), 400
        
        result = self.stock_service.sell_share(symbol, profit)
        
        if result['success']:
            return jsonify({'message': result['message']})
        elif 'not found' in result['error'].lower():
            return jsonify({'error': result['error']}), 404
        else:
            return jsonify({'error': result['error']}), 500
    
    def get_shares(self):
        """Get all shares endpoint."""
        result = self.stock_service.get_all_shares()
        
        if result['success']:
            return jsonify(result['shares'])
        else:
            return jsonify({'error': result['error']}), 500
    
    def search_stock(self):
        """Search for a stock symbol."""
        symbol = request.args.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol parameter required'}), 400
        
        symbol = symbol.strip().upper()
        
        # Search and get price
        result = self.api_service.search_and_get_price(symbol)
        
        if result:
            price_data = result['price_data']
            return jsonify([
                round(price_data.get('ltp', 0), 2),
                [round(price_data.get('open', 0), 2), round(price_data.get('high', 0), 2), result['scrip_code']]
            ])
        
        return jsonify([])
    
    def new_search(self):
        """New search endpoint."""
        symbol = request.args.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol parameter required'}), 400
        
        try:
            result = self.api_service.search_and_get_price(symbol)
            if result:
                price_data = result['price_data']
                return jsonify([int(price_data.get('ltp', 0)), int(price_data.get('open', 0))])
        except Exception as e:
            logger.error(f"Error in new_search: {e}")
        
        return jsonify([])
    
    def get_chart_data(self):
        """Get chart data endpoint (hardcoded to TITAGARH for now)."""
        scrip_code = 'TITAGARH'  # Can be made dynamic
        data = self.api_service.get_chart_data(scrip_code)
        
        if data:
            return jsonify(data)
        return jsonify({'error': 'Unable to fetch chart data'}), 500
    
    def get_live_data(self):
        """Get live data endpoint (hardcoded to TITAGARH for now)."""
        scrip_code = 'TITAGARH'  # Can be made dynamic
        data = self.api_service.get_live_price_data(scrip_code)
        
        if data:
            return jsonify(data)
        return jsonify({'error': 'Unable to fetch live data'}), 500
    
    def get_profit(self):
        """Get total profit endpoint."""
        result = self.stock_service.get_total_profit()
        
        if result['success']:
            return jsonify({'profit': f'{result["profit"]:.2f}'})
        else:
            return jsonify({'error': result['error']}), 500
    
    def health_check(self):
        """Health check endpoint."""
        try:
            from sharemodel import Share
            Share.objects().limit(1).count()
            
            import time
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0',
                'database': 'connected'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            import time
            return jsonify({
                'status': 'unhealthy',
                'timestamp': time.time(),
                'error': str(e)
            }), 503
    
    @staticmethod
    def register(app):
        """Register the blueprint with the Flask app."""
        controller = ShareController()
        app.register_blueprint(controller.blueprint)