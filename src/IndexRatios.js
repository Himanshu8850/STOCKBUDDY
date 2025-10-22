import React, { useState, useEffect, useContext } from "react";
import { AnalyticsIcon } from "./icons";
import { MyContext } from "./context";
const IndexRatios = () => {
  const { chartData, setChartData } = useContext(MyContext);
  const [loading, setLoading] = useState(true);
  const fetchdata = async () => {
    setLoading(true);
    if (!chartData) {
      try {
        const data = await fetch(
          "https://api.moneycontrol.com/mcapi/v1/indices/ad-ratio/full-view?period=1D&sector=&type=MM&sectorSelected=false",
          {
            method: "GET",
          }
        );
        const chari = await data.json();
        console.log(chari.data.chartData);
        setChartData(chari.data.chartData);
        setLoading(false);
      } catch (err) {
        console.error("IndexRatios error:", err);
        setLoading(false);
      }
    } else setLoading(false);
  };

  useEffect(() => {
    fetchdata();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading top performers...</p>
      </div>
    );
  }

  const renderStockCards = (length) => {
    const filteredStocks = chartData
      .filter((stock) => Object.keys(stock).length === length)
      .sort((a, b) => (b.changeP || 0) - (a.changeP || 0));

    if (length === 13) {
      return (
        <div className="stocks-grid">
          {filteredStocks.map((stock, index) => (
            <div className="performance-card" key={stock.id || index}>
              <div className="card-header">
                <div className="rank-badge">#{index + 1}</div>
                <div
                  className={`change-indicator ${
                    stock.changeP >= 0 ? "positive" : "negative"
                  }`}
                >
                  <AnalyticsIcon size={18} />
                </div>
              </div>

              <div className="card-content">
                <h3 className="stock-name">
                  {stock.fullName || "Unknown Stock"}
                </h3>

                <div className="price-section">
                  <div className="current-price">
                    <span className="price-label">LTP</span>
                    <span className="price-value">₹{stock.ltp || "-"}</span>
                  </div>

                  <div className="price-change">
                    <span
                      className={`change-value ${
                        stock.changeP >= 0 ? "positive" : "negative"
                      }`}
                    >
                      {stock.changeP ? `${stock.changeP.toFixed(2)}%` : "-"}
                    </span>
                    <span className="change-amount">
                      {stock.change ? `₹${stock.change.toFixed(2)}` : "-"}
                    </span>
                  </div>
                </div>

                <div className="stock-details">
                  <div className="detail-item">
                    <span className="detail-label">Sector</span>
                    <span className="detail-value">
                      {stock.sector || "N/A"}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Market Cap</span>
                    <span className="detail-value">
                      {stock.mrkCap ? `₹${stock.mrkCap.toFixed(2)}` : "N/A"}
                    </span>
                  </div>
                </div>

                {stock.url && (
                  <div className="card-actions">
                    <a
                      href={stock.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="info-link"
                    >
                      <span className="link-icon">🔗</span>
                      More Info
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (length === 4) {
      return (
        <div className="indices-grid">
          {filteredStocks.map((stock, index) => (
            <div className="index-card" key={stock.id || index}>
              <div className="index-icon">
                <AnalyticsIcon size={36} />
              </div>
              <h4 className="index-name">{stock.name || "Index"}</h4>
              <div className="total-stocks">
                <span className="stocks-count">{stock.totalStocks || 0}</span>
                <span className="stocks-label">Stocks</span>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="stocks-container">
      {chartData && chartData.length > 0 ? (
        <>
          {renderStockCards(13)}

          <div className="section-divider">
            <h3 className="subsection-title">
              <span className="title-icon">
                <AnalyticsIcon size={24} />
              </span>
              Market Indices
            </h3>
          </div>

          {renderStockCards(4)}
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">
            <AnalyticsIcon size={36} />
          </div>
          <h3>No Data Available</h3>
          <p>Unable to fetch top performers data at the moment.</p>
        </div>
      )}
    </div>
  );
};

export default IndexRatios;
