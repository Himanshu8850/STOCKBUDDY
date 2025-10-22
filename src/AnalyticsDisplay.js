import React from "react";
import { MoneyIcon, AnalyticsIcon } from "./icons";

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

  // Formatters for readability and tooltips
  const compactFormatter = new Intl.NumberFormat("en-IN", {
    notation: "compact",
    maximumFractionDigits: 2,
  });
  const currencyFormatter = new Intl.NumberFormat("en-IN");

  // Calculate total value of portfolio
  const totalValue = shares.reduce(
    (total, share) => total + share.price * share.quantity,
    0
  );

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
          <div className="index-icon">
            <MoneyIcon size={28} />
          </div>
          <h4 className="index-name">Total Portfolio Value</h4>
          <div className="total-stocks">
            <span
              className="stocks-count"
              title={`₹${currencyFormatter.format(totalValue)}`}
            >
              ₹{compactFormatter.format(totalValue)}
            </span>
            <span className="stocks-label">Current Value</span>
          </div>
        </div>

        <div className="index-card">
          <div
            className="index-icon"
            style={{ color: totalProfitLoss >= 0 ? "#059669" : "#dc2626" }}
          >
            <AnalyticsIcon size={24} />
          </div>
          <h4 className="index-name">Total Profit/Loss</h4>
          <div className="total-stocks">
            <span
              className="stocks-count"
              style={{ color: totalProfitLoss >= 0 ? "#059669" : "#dc2626" }}
              title={`${
                totalProfitLoss >= 0 ? "+" : "-"
              }₹${currencyFormatter.format(Math.abs(totalProfitLoss))}`}
            >
              {totalProfitLoss >= 0 ? "+" : "-"}₹
              {compactFormatter.format(Math.abs(totalProfitLoss))}
            </span>
            <span className="stocks-label">P&L Amount</span>
          </div>
        </div>

        <div className="index-card">
          <div className="index-icon">
            <AnalyticsIcon size={24} />
          </div>
          <h4 className="index-name">Number of Holdings</h4>
          <div className="total-stocks">
            <span className="stocks-count">{numberOfStocks}</span>
            <span className="stocks-label">Active Stocks</span>
          </div>
        </div>

        <div className="index-card">
          <div
            className="index-icon"
            style={{ color: averagePL >= 0 ? "#059669" : "#dc2626" }}
          >
            <AnalyticsIcon size={24} />
          </div>
          <h4 className="index-name">Average P/L per Stock</h4>
          <div className="total-stocks">
            <span
              className="stocks-count"
              style={{ color: averagePL >= 0 ? "#059669" : "#dc2626" }}
              title={`${averagePL >= 0 ? "+" : "-"}₹${currencyFormatter.format(
                Math.abs(averagePL)
              )}`}
            >
              {averagePL >= 0 ? "+" : "-"}₹
              {compactFormatter.format(Math.abs(averagePL))}
            </span>
            <span className="stocks-label">Per Stock</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDisplay;
