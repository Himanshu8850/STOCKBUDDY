# services/stock_service.py
import time
import logging
from sharemodel import Share, Profit

logger = logging.getLogger(__name__)

class StockService:
    def buy_share(self, symbol, price, quantity):
        """Buy a share (create or update existing)."""
        try:
            existing_share = Share.objects(symbol=symbol).first()
            current_time = time.time()
            
            if existing_share:
                # Update existing share with average price calculation
                total_value = (existing_share.price * existing_share.quantity) + (price * quantity)
                total_quantity = existing_share.quantity + quantity
                existing_share.price = total_value / total_quantity
                existing_share.quantity = total_quantity
                existing_share.created_at = current_time
                existing_share.save()
                
                logger.info(f"Updated share {symbol}: quantity={total_quantity}, avg_price={existing_share.price}")
                return {'success': True, 'message': f'Share updated successfully. ID: {existing_share.id}', 'share_id': str(existing_share.id)}
            else:
                # Create new share
                new_share = Share(
                    symbol=symbol,
                    price=price,
                    quantity=quantity,
                    created_at=current_time
                )
                new_share.save()
                
                logger.info(f"Created new share {symbol}: quantity={quantity}, price={price}")
                return {'success': True, 'message': f'Share bought successfully. ID: {new_share.id}', 'share_id': str(new_share.id)}
                
        except Exception as e:
            logger.error(f"Database error in buy_share: {e}")
            return {'success': False, 'error': 'Database operation failed'}
    
    def sell_share(self, symbol, profit):
        """Sell a share and record profit."""
        try:
            current_time = time.time()
            
            # Update or create profit record
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
                return {'success': True, 'message': 'Share sold successfully'}
            else:
                logger.warning(f"Attempted to sell non-existent share: {symbol}")
                return {'success': False, 'error': 'Share not found in portfolio'}
                
        except Exception as e:
            logger.error(f"Database error in sell_share: {e}")
            return {'success': False, 'error': 'Database operation failed'}
    
    def get_all_shares(self):
        """Get all shares from portfolio."""
        try:
            shares = Share.objects.only('symbol', 'price', 'quantity').all()
            share_list = [
                {
                    'symbol': share.symbol,
                    'price': round(share.price, 2),
                    'quantity': share.quantity,
                }
                for share in shares
            ]
            return {'success': True, 'shares': share_list}
        except Exception as e:
            logger.error(f"Database error in get_all_shares: {e}")
            return {'success': False, 'error': 'Failed to fetch shares'}
    
    def get_total_profit(self):
        """Get total profit from all sold shares."""
        try:
            from mongoengine.queryset.visitor import Q
            pipeline = [
                {'$group': {'_id': None, 'total_profit': {'$sum': '$profit'}}}
            ]
            
            result = list(Profit.objects.aggregate(pipeline))
            total_profit = result[0]['total_profit'] if result else 0
            
            return {'success': True, 'profit': total_profit}
        except Exception as e:
            logger.error(f"Database error in get_total_profit: {e}")
            return {'success': False, 'error': 'Failed to calculate profit'}