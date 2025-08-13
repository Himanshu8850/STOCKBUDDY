from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
from threading import Thread
import smarty
from pymongo import MongoClient
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import json
import logging
from functools import wraps
import os
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pooling for MongoDB
client = MongoClient(maxPoolSize=10, waitQueueTimeoutMS=5000)
app = Flask(__name__)
CORS(app)

# Configuration
app.config['API_TIMEOUT'] = 10  # Timeout for external API calls
app.config['CACHE_TIMEOUT'] = 300  # 5 minutes cache

from sharemodel import Share, Profit
from utils import log_execution_time, validate_symbol, rate_limit

# Add caching and rate limiting decorator
def handle_api_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"API request failed in {f.__name__}: {e}")
            return jsonify({'error': 'External API unavailable'}), 503
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

@app.route('/api/searching', methods=['GET'])
@handle_api_errors
def ge_data():
    symb = request.args.get('symbol')
    if not symb:
        return jsonify({'error': 'Symbol parameter required'}), 400
    
    symb = symb.strip().upper()  # Normalize input
    
    # First API call with timeout
    url = f'https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={symb}&size=1&web=true'
    headers = {'Content-Type': 'application/json'}
    
    response = requests.get(url, headers=headers, timeout=app.config['API_TIMEOUT'])
    
    if response.ok:
        data = response.json()
        if not data.get('data', {}).get('content'):
            return jsonify([])  # No results found
            
        scrip_code = data['data']['content'][0]['nse_scrip_code']
        
        # Second API call with timeout
        price_url = f'https://groww.in/v1/api/stocks_data/v1/tr_live_prices/exchange/NSE/segment/CASH/{scrip_code}/latest'
        
        price_response = requests.get(price_url, headers=headers, timeout=app.config['API_TIMEOUT'])
        
        if price_response.ok:
            price_data = price_response.json()
            result = [
                round(price_data['ltp'], 2),
                [round(price_data['open'], 2), round(price_data['high'], 2), scrip_code]
            ]
            return jsonify(result)
    
    return jsonify([])

@app.route('/buy', methods=['POST'])
@handle_api_errors
def buy_share():
    data = request.get_json()
    
    # Validate input data
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
    url = f'https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={symbol}&size=1&web=true'
    headers = {'Content-Type': 'application/json'}
    
    response = requests.get(url, headers=headers, timeout=app.config['API_TIMEOUT'])
    
    if not response.ok:
        return jsonify({'error': 'Unable to validate symbol'}), 400
    
    search_data = response.json()
    if not search_data.get('data', {}).get('content'):
        return jsonify({'error': 'Invalid symbol'}), 400
        
    scrip_code = search_data['data']['content'][0]['nse_scrip_code']
    
    # Database operation with error handling
    try:
        existing_share = Share.objects(symbol=scrip_code).first()
        current_time = time.time()
        
        if existing_share:
            # Update existing share with average price calculation
            total_value = (existing_share.price * existing_share.quantity) + (price * quantity)
            total_quantity = existing_share.quantity + quantity
            existing_share.price = total_value / total_quantity
            existing_share.quantity = total_quantity
            existing_share.created_at = current_time
            existing_share.save()
            
            logger.info(f"Updated share {scrip_code}: quantity={total_quantity}, avg_price={existing_share.price}")
            return jsonify({'message': f'Share updated successfully. ID: {existing_share.id}'})
        else:
            # Create new share
            new_share = Share(
                symbol=scrip_code,
                price=price,
                quantity=quantity,
                created_at=current_time
            )
            new_share.save()
            
            logger.info(f"Created new share {scrip_code}: quantity={quantity}, price={price}")
            return jsonify({'message': f'Share bought successfully. ID: {new_share.id}'})
            
    except Exception as e:
        logger.error(f"Database error in buy_share: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/sell', methods=['DELETE'])
@handle_api_errors
def delete_share():
    symbol = request.args.get('symbol')
    profit_str = request.args.get('profit')
    
    if not symbol or profit_str is None:
        return jsonify({'error': 'Missing required parameters: symbol, profit'}), 400
    
    try:
        profit = float(profit_str)
        symbol = symbol.strip().upper()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid profit value'}), 400
    
    try:
        # Update or create profit record
        current_time = time.time()
        profit_doc = Profit.objects(symbol=symbol).first()
        
        if profit_doc:
            profit_doc.profit += profit
            profit_doc.last_updated = current_time
        else:
            profit_doc = Profit(symbol=symbol, profit=profit, last_updated=current_time)
        
        profit_doc.save()
        
        # Delete share record
        share_to_delete = Share.objects(symbol=symbol).first()
        if share_to_delete:
            share_to_delete.delete()
            logger.info(f"Sold share {symbol} with profit {profit}")
            return jsonify({'message': 'Share sold successfully'})
        else:
            logger.warning(f"Attempted to sell non-existent share: {symbol}")
            return jsonify({'error': 'Share not found in portfolio'}), 404
            
    except Exception as e:
        logger.error(f"Database error in delete_share: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/profit', methods=['GET'])
@handle_api_errors
def share_profit():
    try:
        # Use aggregation for better performance
        pipeline = [
            {'$group': {'_id': None, 'total_profit': {'$sum': '$profit'}}}
        ]
        
        result = list(Profit.objects.aggregate(pipeline))
        total_profit = result[0]['total_profit'] if result else 0
        
        return jsonify({'profit': f'{total_profit:.2f}'})
        
    except Exception as e:
        logger.error(f"Database error in share_profit: {e}")
        return jsonify({'error': 'Failed to calculate profit'}), 500

@app.route('/shares', methods=['GET'])
@handle_api_errors
def main_page():
    try:
        # Optimized query with only required fields
        shares = Share.objects.only('symbol', 'price', 'quantity').all()
        
        share_list = [
            {
                'symbol': share.symbol,
                'price': round(share.price, 2),
                'quantity': share.quantity,
            }
            for share in shares
        ]
        
        return jsonify(share_list)
        
    except Exception as e:
        logger.error(f"Database error in main_page: {e}")
        return jsonify({'error': 'Failed to fetch shares'}), 500


@app.route('/api/new-search', methods=['GET'])
def new_search():
    symb = request.args.get('symbol')
    # Note: scrapsymb function is not defined - implementing basic search functionality
    try:
        url = f'https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={symb}&size=1&web=true'
        headers = {
            'Content-Type': 'application/json',
        }
        res = requests.get(url, headers=headers)
        if res.ok:
            res_data = res.json()
            scrip_code = res_data['data']['content'][0]['nse_scrip_code']
            
            # Get latest price data
            price_url = f'https://groww.in/v1/api/stocks_data/v1/tr_live_prices/exchange/NSE/segment/CASH/{scrip_code}/latest'
            price_res = requests.get(price_url, headers=headers)
            
            if price_res.ok:
                price_data = price_res.json()
                result = [int(price_data['ltp']), int(price_data['open'])]
                return jsonify(result)
    except Exception as e:
        print(f"Error in new_search: {e}")
        
    return jsonify([])

@app.route('/api/old-data', methods=['GET'])
def graphdata():
    url='https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/TITAGARH/daily?intervalInMinutes=1&minimal=true'
    headers={
        'Content-Type':'application/json'
    }
    data=requests.get(url,headers=headers)
    if data.ok:
        return data.json()
    return 'sorry'

@app.route('/api/live', methods=['GET'])
def graphdatalive():
    url='https://groww.in/v1/api/stocks_data/v1/tr_live_prices/exchange/NSE/segment/CASH/TITAGARH/latest'
    headers={
        'Content-Type':'application/json'
    }
    data=requests.get(url,headers=headers)
    if data.ok:
        z=data.json()
        dat=[z['ltp'],z['tsInMillis']]
        return [z['tsInMillis'],z['ltp']]
    return 'sorry'

@app.route('/api/model', methods=['GET'])
@handle_api_errors
@log_execution_time
def modelhandler():
    try:
        # Use hardcoded symbol for now, can be parameterized later
        symbol = request.args.get('symbol', 'TITAGARH')
        
        url = f'{app.config.get("GROWW_CHART_URL", "https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH")}/{symbol}/daily?intervalInMinutes=5'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, timeout=app.config['API_TIMEOUT'])
        
        if response.ok:
            data = response.json()
            candles = data.get('candles', [])
            
            if not candles:
                return jsonify({'error': 'No data available for prediction'}), 404
            
            # Use optimized prediction engine
            from model_utils import prediction_engine
            
            # Convert candles to numpy array format expected by the model
            candles_array = np.array(candles)
            
            prediction_result = prediction_engine.predict_trend(candles_array)
            
            return jsonify({
                'symbol': symbol,
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['confidence'],
                'timestamp': time.time(),
                'data_points': len(candles)
            })
        else:
            logger.warning(f"Failed to fetch chart data for {symbol}")
            return jsonify({'error': 'Unable to fetch market data'}), 503
            
    except Exception as e:
        logger.error(f"Model prediction error: {e}")
        return jsonify({'error': 'Prediction service unavailable'}), 500

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        Share.objects().limit(1).count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': time.time(),
            'error': str(e)
        }), 503

if __name__ == '__main__':
    from config import get_config
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
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