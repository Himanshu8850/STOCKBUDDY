from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
from pymongo import MongoClient
import json
import logging
from functools import wraps
import os
import re
from sharemodel import Share, Profit

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
client = MongoClient(maxPoolSize=10, waitQueueTimeoutMS=5000)
app = Flask(__name__)
# Configure CORS explicitly for frontend origin and API routes
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:37839"]}},
    methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Gemini configuration (prefer environment variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Helper to get Gemini AI prediction for a single stock
def get_gemini_prediction(stock):
    prompt = f"""
    You are an equities analyst focused on swing trading (1-4 weeks horizon).
    Analyze the following stock and provide:
    - 2 pros (swing-trade relevant: momentum, catalysts, support/resistance, volume, risk/reward)
    - 2 cons (risks: earnings/catalyst risk, volatility, overhead supply, macro headwinds)
    - A verdict: strictly one of "Swing Buy", "Neutral", or "Avoid" followed by a brief reason in the same string
    Stock: {stock}
    Return ONLY valid JSON with keys exactly: pros (array of strings), cons (array of strings), verdict (string). No markdown, no code fences, no extra text.
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }
    try:
        if not GEMINI_API_KEY:
            return {"pros": [], "cons": [], "verdict": "AI error: Missing GEMINI_API_KEY/GOOGLE_API_KEY env"}

        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=40)
        if response.ok:
            result = response.json()
            # Parse Gemini's response
            try:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                # Fall back to a simpler extraction if structure differs
                text = json.dumps(result)

            # Normalize possible markdown fences and extract JSON
            cleaned = re.sub(r"```(?:json|JSON)?", "", text)
            cleaned = cleaned.replace("```", "").strip()

            # Try direct JSON parse
            try:
                parsed = json.loads(cleaned)
            except Exception:
                # Try to extract the first JSON object from the text
                start = cleaned.find('{')
                end = cleaned.rfind('}')
                if start != -1 and end != -1 and end > start:
                    snippet = cleaned[start:end+1]
                    try:
                        parsed = json.loads(snippet)
                    except Exception:
                        parsed = None
                else:
                    parsed = None

            if isinstance(parsed, dict):
                pros = parsed.get('pros') if isinstance(parsed.get('pros'), list) else []
                cons = parsed.get('cons') if isinstance(parsed.get('cons'), list) else []
                verdict = parsed.get('verdict') if isinstance(parsed.get('verdict'), str) else ""
                return {"pros": pros, "cons": cons, "verdict": verdict or ""}

            # Fallback: return raw text in verdict
            return {"pros": [], "cons": [], "verdict": cleaned}
        else:
            try:
                err_text = response.text[:500]
            except Exception:
                err_text = ""
            logger.error(f"Gemini API error {response.status_code}: {err_text}")
            return {"pros": [], "cons": [], "verdict": f"AI error: {response.status_code}"}
    except Exception as e:
        logger.exception("Gemini API call failed")
        return {"pros": [], "cons": [], "verdict": f"Error: {e}"}


def _parse_gemini_text_to_json(text: str):
    """Best-effort parser to extract JSON from Gemini text responses, handling code fences."""
    cleaned = re.sub(r"```(?:json|JSON)?", "", text)
    cleaned = cleaned.replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            snippet = cleaned[start:end + 1]
            try:
                return json.loads(snippet)
            except Exception:
                return None
        return None


# Helper to get Gemini AI predictions for a batch of stocks
def get_gemini_predictions_batch(stocks_batch):
    """Ask Gemini for predictions for multiple stocks in one request.
    Returns a dict: { symbol: {pros:[], cons:[], verdict:str}, ... }
    """
    # Build batch prompt
    stocks_csv = ", ".join(stocks_batch)
    prompt = f"""
    You are an equities analyst focused on swing trading (1-4 weeks horizon).
    For EACH of the following stocks: {stocks_csv}
    provide:
    - 2 pros (swing-trade relevant: momentum, catalysts, S/R, volume, risk/reward)
    - 2 cons (risks: earnings/catalyst risk, volatility, overhead supply, macro)
    - A verdict: strictly one of "Swing Buy", "Neutral", or "Avoid" followed by a brief reason in the same string
    Return ONLY a single JSON object mapping each stock symbol to an object with keys pros (array), cons (array), verdict (string). No markdown, no code fences, no extra text.
    Example format only:
    {{
      "TCS": {{"pros": ["..."], "cons": ["..."], "verdict": "Swing Buy - reason"}},
      "INFY": {{"pros": ["..."], "cons": ["..."], "verdict": "Neutral - reason"}}
    }}
    """

    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

    if not GEMINI_API_KEY:
        # Return error objects for all symbols
        return {sym: {"pros": [], "cons": [], "verdict": "AI error: Missing GEMINI_API_KEY/GOOGLE_API_KEY env"} for sym in stocks_batch}

    # Simple retry for transient overloads
    max_retries = 3
    backoff_seconds = 1
    last_status_code = None
    for attempt in range(max_retries):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=70)
            if response.ok:
                result = response.json()
                try:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    text = json.dumps(result)
                parsed = _parse_gemini_text_to_json(text)
                if isinstance(parsed, dict):
                    # Normalize each entry
                    normalized = {}
                    for sym in stocks_batch:
                        payload = parsed.get(sym) or parsed.get(sym.upper()) or parsed.get(sym.lower())
                        if isinstance(payload, dict):
                            pros = payload.get('pros') if isinstance(payload.get('pros'), list) else []
                            cons = payload.get('cons') if isinstance(payload.get('cons'), list) else []
                            verdict = payload.get('verdict') if isinstance(payload.get('verdict'), str) else ""
                            normalized[sym] = {"pros": pros, "cons": cons, "verdict": verdict}
                        else:
                            normalized[sym] = {"pros": [], "cons": [], "verdict": "AI error: malformed batch item"}
                    return normalized
                # Fallback: one error entry for all
                return {sym: {"pros": [], "cons": [], "verdict": "AI error: invalid response"} for sym in stocks_batch}
            else:
                # 503 or others
                last_status_code = response.status_code
                logger.error(f"Gemini API error {response.status_code}: {response.text[:500]}")
                if response.status_code == 503 and attempt < max_retries - 1:
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                break
        except Exception as e:
            logger.exception("Gemini batch call failed")
            if attempt < max_retries - 1:
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                continue
            last_status_code = 500
            break
    # Fallback: call per-symbol to improve reliability (helps with 503 overload)
    fallback_results = {}
    for sym in stocks_batch:
        fallback_results[sym] = get_gemini_prediction(sym)
        time.sleep(0.4)
    # If everything failed, annotate with status code
    if all((r.get('verdict','').lower().startswith('ai error') or r.get('verdict','').lower().startswith('error')) for r in fallback_results.values()):
        code = last_status_code or 'unknown'
        return {sym: {"pros": [], "cons": [], "verdict": f"AI error: {code}"} for sym in stocks_batch}
    return fallback_results

# New endpoint for AI predictions
@app.route('/api/ai-predictions', methods=['POST', 'OPTIONS'])
def ai_predictions():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json()
    stocks = data.get('stocks', [])
    if not stocks or not isinstance(stocks, list):
        return jsonify({'error': 'No stocks provided'}), 400

    # Process in batches of 2 symbols to improve reliability
    batch_size = 2
    results = {}
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i + batch_size]
        batch_result = get_gemini_predictions_batch(batch)
        results.update(batch_result)
        # Small delay between batches to avoid rate spikes
        time.sleep(0.5)
    return jsonify(results)


 

# Configuration
app.config['API_TIMEOUT'] = 10  # Timeout for external API calls
app.config['CACHE_TIMEOUT'] = 300  # 5 minutes cache

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