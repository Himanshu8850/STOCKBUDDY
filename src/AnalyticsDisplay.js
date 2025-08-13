import React from 'react';

const AnalyticsDisplay = ({ shares }) => {
  // Handle null/undefined shares
  if (!shares || !Array.isArray(shares)) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading portfolio analytics...</p>
      </div>
    );
  }

  // Calculate total value of portfolio
  const totalValue = shares.reduce((total, share) => {
    return total + (share.price * share.quantity);
  }, 0);

  // Calculate total profit/loss
  const totalProfitLoss = shares.reduce((total, share) => {
    if (share.profit && share.profit.length > 0) {
      return total + share.profit[0];
    }
    return total;
  }, 0);

  // Calculate number of stocks
  const numberOfStocks = shares.length;

  const averagePL = numberOfStocks > 0 ? totalProfitLoss / numberOfStocks : 0;

  return (
    <div className="stocks-container">
      <div className="indices-grid">
        <div className="index-card">
          <div className="index-icon">💰</div>
          <h4 className="index-name">Total Portfolio Value</h4>
          <div className="total-stocks">
            <span className="stocks-count">₹{totalValue.toFixed(2)}</span>
            <span className="stocks-label">Current Value</span>
          </div>
        </div>

        <div className="index-card">
          <div className="index-icon" style={{ color: totalProfitLoss >= 0 ? '#059669' : '#dc2626' }}>
            {totalProfitLoss >= 0 ? '📈' : '📉'}
          </div>
          <h4 className="index-name">Total Profit/Loss</h4>
          <div className="total-stocks">
            <span 
              className="stocks-count" 
              style={{ color: totalProfitLoss >= 0 ? '#059669' : '#dc2626' }}
            >
              {totalProfitLoss >= 0 ? '+' : ''}₹{Math.abs(totalProfitLoss).toFixed(2)}
            </span>
            <span className="stocks-label">P&L Amount</span>
          </div>
        </div>

        <div className="index-card">
          <div className="index-icon">🎯</div>
          <h4 className="index-name">Number of Holdings</h4>
          <div className="total-stocks">
            <span className="stocks-count">{numberOfStocks}</span>
            <span className="stocks-label">Active Stocks</span>
          </div>
        </div>

        <div className="index-card">
          <div className="index-icon" style={{ color: averagePL >= 0 ? '#059669' : '#dc2626' }}>
            {averagePL >= 0 ? '⭐' : '⚠️'}
          </div>
          <h4 className="index-name">Average P/L per Stock</h4>
          <div className="total-stocks">
            <span 
              className="stocks-count" 
              style={{ color: averagePL >= 0 ? '#059669' : '#dc2626' }}
            >
              {averagePL >= 0 ? '+' : ''}₹{Math.abs(averagePL).toFixed(2)}
            </span>
            <span className="stocks-label">Per Stock</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDisplay;