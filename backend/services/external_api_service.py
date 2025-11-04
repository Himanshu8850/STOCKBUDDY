import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self):
        self.timeout = Config.API_TIMEOUT
        self.search_url = Config.GROWW_SEARCH_URL
        self.price_url = Config.GROWW_PRICE_URL
        self.chart_url = Config.GROWW_CHART_URL
    
    def search_stock(self, symbol):
        """Search for a stock symbol and get its scrip code."""
        url = f'{self.search_url}?page=0&query={symbol}&size=1&web=true'
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.ok:
                data = response.json()
                if data.get('data', {}).get('content'):
                    return data['data']['content'][0]['nse_scrip_code']
            return None
        except Exception as e:
            logger.error(f"Error searching stock {symbol}: {e}")
            return None
    
    def get_stock_price(self, scrip_code):
        """Get current stock price for a scrip code."""
        url = f'{self.price_url}/{scrip_code}/latest'
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.ok:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting price for {scrip_code}: {e}")
            return None
    
    def search_and_get_price(self, symbol):
        """Search for stock and get its price in one call."""
        scrip_code = self.search_stock(symbol)
        if not scrip_code:
            return None
        
        price_data = self.get_stock_price(scrip_code)
        if not price_data:
            return None
        
        return {
            'scrip_code': scrip_code,
            'price_data': price_data
        }
    
    def get_chart_data(self, scrip_code, interval_in_minutes=1):
        """Get historical chart data for a stock."""
        url = f'{self.chart_url}/{scrip_code}/daily?intervalInMinutes={interval_in_minutes}&minimal=true'
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.ok:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting chart data for {scrip_code}: {e}")
            return None
    
    def get_live_price_data(self, scrip_code):
        """Get live price data for a stock."""
        price_data = self.get_stock_price(scrip_code)
        if price_data:
            return [price_data.get('tsInMillis', 0), price_data.get('ltp', 0)]
        return None