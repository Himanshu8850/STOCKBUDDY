import numpy as np
import pandas as pd
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)  # Cache computed features for repeated calculations
def compute_features(tr, fut, data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error
    import datetime
    import json
    
    try:
        scaler = MinMaxScaler()
        
        # Convert data to numpy array if not already
        if isinstance(data, str):
            # Handle string input (file path)
            data = np.loadtxt(data)
        else:
            data = np.array(data)
        
        logger.info(f"Processing data with shape: {data.shape}")
        
        # Vectorized operations for better performance
        future = []
        for i in range(len(data) - fut):
            price_changes = (data[i:i+fut+1, 4] - data[i, 4]) / data[i, 4]
            pos = np.sum(price_changes >= 0.01)
            neg = np.sum(price_changes <= -0.01)
            
            if pos > neg:
                future.append(1)
            elif neg > pos:
                future.append(-1)
            else:
                future.append(0)
        
        # Vectorized computation for summ
        summ = []
        sumi = 0
        for i in range(fut, len(data)):
            price_changes = (data[i, 4] - data[i-fut:i+1, 4]) / data[i, 4]
            pos = np.sum(price_changes >= 0.01)
            neg = np.sum(price_changes <= -0.01)
            summ.append(sumi)
            
            if pos > neg:
                sumi += 1
            elif neg > pos:
                sumi -= 1
        
        # Pad arrays to match data length
        future = future + [5] * fut
        summ = [np.nan] * fut + summ
        
        # Efficient timestamp transformation
        def transform_timestamp(timestamp):
            dt = datetime.datetime.utcfromtimestamp(timestamp)
            new_dt = datetime.datetime(1970, 1, 1, dt.hour, dt.minute)
            return int(new_dt.timestamp())
        
        # Normalize data in chunks for memory efficiency
        chunk_size = 72
        for i in range(0, len(data) - chunk_size, chunk_size):
            end_idx = min(i + chunk_size, len(data))
            data[i:end_idx] = scaler.fit_transform(data[i:end_idx]) + 1
        
        # Create DataFrame
        data = np.column_stack((data, summ, future))
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'summ', 'future'])
        
        # Efficient technical indicator calculations
        # Moving Averages
        df['SMA_5'] = df['close'].rolling(window=tr, min_periods=1).mean()
        df['SMA_10'] = df['close'].rolling(window=tr*2, min_periods=1).mean()
        
        # Exponential Moving Averages
        df['EMA_5'] = df['close'].ewm(span=tr, adjust=False).mean()
        df['EMA_10'] = df['close'].ewm(span=tr*2, adjust=False).mean()
        
        # RSI calculation (optimized)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=tr, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=tr, min_periods=1).mean()
        rs = gain / loss.replace(0, np.inf)  # Handle division by zero
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=tr, adjust=False).mean()
        ema_26 = df['close'].ewm(span=tr*2, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=tr*2, min_periods=1).mean()
        rolling_std = df['close'].rolling(window=tr*2, min_periods=1).std()
        df['BB_Upper'] = df['BB_Middle'] + (2 * rolling_std)
        df['BB_Lower'] = df['BB_Middle'] - (2 * rolling_std)
        
        # On-Balance Volume (OBV)
        df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        # True Range and ATR (vectorized)
        df['H-L'] = df['high'] - df['low']
        df['H-PC'] = (df['high'] - df['close'].shift(1)).abs()
        df['L-PC'] = (df['low'] - df['close'].shift(1)).abs()
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=tr*6, min_periods=1).mean()
        
        # Price Rate of Change and Momentum
        df['ROC'] = df['close'].pct_change(periods=tr)
        df['Momentum'] = df['close'].diff(tr)
        df['Std_Dev'] = df['close'].rolling(window=tr*2, min_periods=1).std()
        
        # Clean up and organize data
        future_column = df['future']
        df = df.drop(columns=['future'])
        df['future'] = future_column
        timestamp_column = df['timestamp']
        
        # Drop rows with excessive NaN values
        df = df.dropna(thresh=len(df.columns) * 0.7)  # Keep rows with at least 70% non-NaN values
        df = df.reset_index(drop=True)
        
        # Save processed data
        df.to_csv('dfinal.csv', index=False)
        
        logger.info(f"Feature computation completed. Final shape: {df.shape}")
        return df, timestamp_column
        
    except Exception as e:
        logger.error(f"Error in compute_features: {e}")
        raise

def modelhandle(data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error
    import json
    from keras.models import load_model
    import datetime
    import pytz
    from PIL import Image

    tr = 12
    fut = 12
    freedom = 2
    df_with_features,timi = compute_features(tr, fut, data)

    # Load the LSTM model
    model = load_model(f'{tr}_{fut}min(pro3).keras')
    fut += freedom
    data = df_with_features
    closes=df_with_features['close']
    data = np.array(data)

    def transform_timestamp(timestamp):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        new_dt = datetime.datetime(1970, 1, 1, dt.hour, dt.minute)
        new_timestamp = int(new_dt.timestamp())
        return new_timestamp

    data = np.array(data)
    # scaler.fit(data)
    future = data[1:, -1]
    data = data[1:, :-1]
    print(data)
    label_mapping = {0: "sell", 1: "hold", 2: "buy"}
    predictions = model.predict(data)
    pred = np.argmax(predictions, axis=1)
    pred = [label_mapping[label] for label in pred]
    closes=np.array(closes)
    pred=np.column_stack((pred,future,timi[1:],closes[1:]))
    pred_list = pred.tolist()
    return pred_list
