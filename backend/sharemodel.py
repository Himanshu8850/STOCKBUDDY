from mongoengine import Document, StringField, FloatField, IntField, connect
import os

# Use environment variable for MongoDB URI for better security
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://text:123@cluster0.stfphmt.mongodb.net/')
connect('Shares', host=MONGODB_URI)

class Share(Document):
    symbol = StringField(required=True, max_length=10, db_index=True)  # Added index for faster queries
    price = FloatField(required=True, min_value=0)  # Added validation
    quantity = IntField(required=True, min_value=0)  # Added validation
    created_at = FloatField()  # Added timestamp for tracking
    
    meta = {
        'indexes': [
            'symbol',  # Index on symbol for faster lookups
            ('symbol', 'created_at'),  # Compound index
        ]
    }

class Profit(Document):
    symbol = StringField(required=True, max_length=10, db_index=True)
    profit = FloatField(default=0.0)  # Changed to Float for decimal precision
    last_updated = FloatField()  # Added timestamp
    
    meta = {
        'indexes': ['symbol']  # Index for faster queries
    }

