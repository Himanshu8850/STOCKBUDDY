"""
Model utilities for optimized batch processing
"""
import numpy as np
import logging
from functools import lru_cache
import threading

logger = logging.getLogger(__name__)

class ModelManager:
    """Singleton model manager for efficient model loading and caching"""
    _instance = None
    _lock = threading.Lock()
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self, model_path):
        """Load model with caching"""
        if model_path not in self._models:
            try:
                from keras.models import load_model
                self._models[model_path] = load_model(model_path)
                logger.info(f"Model loaded: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model {model_path}: {e}")
                raise
        return self._models[model_path]
    
    def predict_batch(self, model_path, data_batch, batch_size=32):
        """Batch prediction for better performance"""
        model = self.load_model(model_path)
        
        if len(data_batch) <= batch_size:
            return model.predict(data_batch)
        
        # Process in batches
        predictions = []
        for i in range(0, len(data_batch), batch_size):
            batch = data_batch[i:i + batch_size]
            batch_pred = model.predict(batch)
            predictions.append(batch_pred)
        
        return np.vstack(predictions)
    
    def clear_cache(self):
        """Clear model cache"""
        self._models.clear()
        logger.info("Model cache cleared")

class DataProcessor:
    """Optimized data processing utilities"""
    
    @staticmethod
    @lru_cache(maxsize=100)
    def calculate_technical_indicators(prices_tuple, window=14):
        """Cached technical indicator calculation"""
        prices = np.array(prices_tuple)
        
        if len(prices) < window:
            return None
        
        # RSI calculation
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.convolve(gains, np.ones(window)/window, mode='valid')
        avg_losses = np.convolve(losses, np.ones(window)/window, mode='valid')
        
        rs = avg_gains / np.where(avg_losses == 0, 1e-10, avg_losses)
        rsi = 100 - (100 / (1 + rs))
        
        # Moving averages
        sma = np.convolve(prices, np.ones(window)/window, mode='valid')
        
        return {
            'rsi': rsi[-1] if len(rsi) > 0 else 50,
            'sma': sma[-1] if len(sma) > 0 else prices[-1],
            'momentum': (prices[-1] - prices[-window]) / prices[-window] * 100 if len(prices) >= window else 0
        }
    
    @staticmethod
    def normalize_batch(data_batch, method='minmax'):
        """Batch normalization"""
        if method == 'minmax':
            min_vals = np.min(data_batch, axis=0)
            max_vals = np.max(data_batch, axis=0)
            return (data_batch - min_vals) / (max_vals - min_vals + 1e-8)
        elif method == 'zscore':
            mean_vals = np.mean(data_batch, axis=0)
            std_vals = np.std(data_batch, axis=0)
            return (data_batch - mean_vals) / (std_vals + 1e-8)
        else:
            return data_batch
    
    @staticmethod
    def create_sequences(data, sequence_length, target_col=-1):
        """Create sequences for time series data"""
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length), :-1])  # All columns except target
            y.append(data[i + sequence_length, target_col])  # Target column
        return np.array(X), np.array(y)

class PredictionEngine:
    """Optimized prediction engine"""
    
    def __init__(self, model_path='12_12min(pro3).keras'):
        self.model_manager = ModelManager()
        self.model_path = model_path
        self.data_processor = DataProcessor()
    
    def predict_trend(self, price_data, additional_features=None):
        """Predict stock trend with optimized processing"""
        try:
            # Prepare features
            if isinstance(price_data, list):
                price_data = np.array(price_data)
            
            # Add technical indicators
            if len(price_data) >= 14:
                prices_tuple = tuple(price_data[:, 4])  # Close prices
                indicators = self.data_processor.calculate_technical_indicators(prices_tuple)
                
                if indicators:
                    # Add indicators as features
                    indicator_array = np.array([
                        indicators['rsi'],
                        indicators['sma'],
                        indicators['momentum']
                    ])
                    
                    # Extend features
                    extended_features = np.column_stack([
                        price_data,
                        np.tile(indicator_array, (len(price_data), 1))
                    ])
                else:
                    extended_features = price_data
            else:
                extended_features = price_data
            
            # Normalize data
            normalized_data = self.data_processor.normalize_batch(extended_features)
            
            # Make prediction
            predictions = self.model_manager.predict_batch(
                self.model_path,
                normalized_data.reshape(1, -1)
            )
            
            # Convert to readable format
            pred_class = np.argmax(predictions, axis=1)[0]
            confidence = np.max(predictions, axis=1)[0]
            
            label_mapping = {0: "sell", 1: "hold", 2: "buy"}
            
            return {
                'prediction': label_mapping.get(pred_class, "hold"),
                'confidence': float(confidence),
                'raw_predictions': predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'prediction': "hold",
                'confidence': 0.5,
                'error': str(e)
            }
    
    def batch_predict(self, multiple_stocks_data):
        """Batch prediction for multiple stocks"""
        results = {}
        
        for symbol, data in multiple_stocks_data.items():
            try:
                result = self.predict_trend(data)
                results[symbol] = result
            except Exception as e:
                logger.error(f"Error predicting for {symbol}: {e}")
                results[symbol] = {
                    'prediction': "hold",
                    'confidence': 0.5,
                    'error': str(e)
                }
        
        return results

# Global prediction engine instance
prediction_engine = PredictionEngine()
