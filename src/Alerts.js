import React, { useState, useEffect, useContext } from "react";
import { AnalyticsIcon } from "./icons";
import Modal from "react-modal";
import { MyContext } from "./context";

const IndexRatios = () => {
  const { chart, setChart } = useContext(MyContext);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState(null);

  useEffect(() => {
    setLoading(true);
    const fetchData = async () => {
      if (!chart) {
        try {
          const response = await fetch(
            "https://api.moneycontrol.com/mcapi/v1/fys/api/v1/stockfeeds/page?alerts=PRICE_ALERT%2CNEWS%2CANNOUNCEMENT%2CCORPORATE_ACTION%2CRESULT%2CTECHNICAL_ANALYSIS%2CDERIVATIVES%2CDEAL%2CSHAREHOLDING%2CRESEARCH&forward=true&index=7&list=MCCURATED&size=10"
          );
          const data = await response.json();
          console.log("fetchhhhhhhhh");
          const chart = data.data.list; // Adjusted to new data structure
          setChart(chart);
          setLoading(false);
        } catch (error) {
          console.error("Error fetching Alerts:", error);
          setLoading(false);
        }
      } else {
        setChart(chart);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const openModal = (stock) => {
    setSelectedStock(stock);
  };

  const closeModal = () => {
    setSelectedStock(null);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading alerts...</p>
      </div>
    );
  }

  return (
    <div className="stocks-container">
      {Array.isArray(chart) && chart.length > 0 ? (
        <div className="stocks-grid">
          {chart
            .sort(
              (a, b) =>
                parseFloat(b.percentchange) - parseFloat(a.percentchange)
            )
            .map((stock, index) => (
              <div
                className="performance-card"
                key={stock.scId}
                onClick={() => openModal(stock)}
                style={{ cursor: "pointer" }}
              >
                <div className="card-header">
                  <div className="rank-badge">#{index + 1}</div>
                  <div
                    className={`change-indicator ${
                      stock.percentchange >= 0 ? "positive" : "negative"
                    }`}
                  >
                    <AnalyticsIcon size={18} />
                  </div>
                </div>

                <div className="card-content">
                  <h3 className="stock-name">
                    {stock.fullName || stock.shortName || "Unknown Stock"}
                  </h3>

                  <div className="price-section">
                    <div className="current-price">
                      <span className="price-label">Price</span>
                      <span className="price-value">₹{stock.price || "-"}</span>
                    </div>

                    <div className="price-change">
                      <span
                        className={`change-value ${
                          stock.percentchange >= 0 ? "positive" : "negative"
                        }`}
                      >
                        {stock.percentchange
                          ? `${parseFloat(stock.percentchange).toFixed(2)}%`
                          : "-"}
                      </span>
                      <span className="change-amount">
                        {stock.change
                          ? `₹${parseFloat(stock.change).toFixed(2)}`
                          : "-"}
                      </span>
                    </div>
                  </div>

                  <div className="stock-details">
                    <div className="detail-item">
                      <span className="detail-label">Exchange</span>
                      <span className="detail-value">
                        {stock.exchg || "N/A"}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Followers</span>
                      <span className="detail-value">
                        {stock.followerCount || 0}
                      </span>
                    </div>
                  </div>

                  {stock.pncUrl && (
                    <div className="card-actions">
                      <a
                        href={stock.pncUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="info-link"
                        onClick={(e) => e.stopPropagation()}
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
      ) : (
        <div className="empty-state">
          <div className="empty-icon">🚨</div>
          <h3>No Alerts Available</h3>
          <p>Unable to fetch market alerts at the moment.</p>
        </div>
      )}

      {selectedStock && (
        <Modal
          isOpen={!!selectedStock}
          onRequestClose={closeModal}
          contentLabel="Stock Details"
          ariaHideApp={false}
          style={{
            content: {
              top: "50%",
              left: "50%",
              right: "auto",
              bottom: "auto",
              marginRight: "-50%",
              transform: "translate(-50%, -50%)",
              width: "500px",
              maxHeight: "80vh",
              overflowY: "auto",
              background: "rgba(255, 255, 255, 0.95)",
              borderRadius: "20px",
              border: "1px solid rgba(255, 255, 255, 0.8)",
              backdropFilter: "blur(10px)",
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.1)",
            },
            overlay: {
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              backdropFilter: "blur(5px)",
            },
          }}
        >
          <div style={{ padding: "1rem" }}>
            <div className="card-header" style={{ marginBottom: "1.5rem" }}>
              <h2 className="stock-name">
                {selectedStock.fullName || selectedStock.shortName}
              </h2>
              <div
                className={`change-indicator ${
                  selectedStock.percentchange >= 0 ? "positive" : "negative"
                }`}
              >
                <AnalyticsIcon size={18} />
              </div>
            </div>

            <div className="price-section" style={{ marginBottom: "1.5rem" }}>
              <div className="current-price">
                <span className="price-label">Price</span>
                <span className="price-value">₹{selectedStock.price}</span>
              </div>
              <div className="price-change">
                <span
                  className={`change-value ${
                    selectedStock.percentchange >= 0 ? "positive" : "negative"
                  }`}
                >
                  {selectedStock.percentchange}%
                </span>
                <span className="change-amount">₹{selectedStock.change}</span>
              </div>
            </div>

            <div className="stock-details" style={{ marginBottom: "1.5rem" }}>
              <div className="detail-item">
                <span className="detail-label">Exchange</span>
                <span className="detail-value">{selectedStock.exchg}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Followers</span>
                <span className="detail-value">
                  {selectedStock.followerCount}
                </span>
              </div>
            </div>

            {selectedStock.pncUrl && (
              <div className="card-actions" style={{ marginBottom: "1.5rem" }}>
                <a
                  href={selectedStock.pncUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="info-link"
                >
                  <span className="link-icon">🔗</span>
                  More Info
                </a>
              </div>
            )}

            {selectedStock.feeds && (
              <div style={{ marginBottom: "1.5rem" }}>
                <h3 style={{ color: "#1f2937", marginBottom: "1rem" }}>
                  Feeds:
                </h3>
                {Object.entries(selectedStock.feeds).map(
                  ([feedType, feedData]) => (
                    <div key={feedType} style={{ marginBottom: "1rem" }}>
                      <h4 style={{ color: "#667eea", marginBottom: "0.5rem" }}>
                        {feedType}
                      </h4>
                      {Array.isArray(feedData) &&
                        feedData.map((feed, index) => (
                          <div key={index} style={{ marginBottom: "0.5rem" }}>
                            <h5
                              style={{ color: "#64748b", fontSize: "0.9rem" }}
                            >
                              {feed.subCategory}
                            </h5>
                            {feed.data &&
                              Array.isArray(feed.data.dataList) &&
                              feed.data.dataList.map((item, idx) => (
                                <div
                                  key={idx}
                                  style={{
                                    padding: "0.5rem",
                                    background: "#f8fafc",
                                    borderRadius: "8px",
                                    margin: "0.25rem 0",
                                  }}
                                >
                                  {Object.entries(item).map(
                                    ([key, value]) =>
                                      (key === "action" ||
                                        key === "fullName") && (
                                        <p
                                          key={key}
                                          style={{
                                            margin: "0.25rem 0",
                                            fontSize: "0.85rem",
                                          }}
                                        >
                                          <strong>{key}:</strong> {value}
                                        </p>
                                      )
                                  )}
                                </div>
                              ))}
                          </div>
                        ))}
                    </div>
                  )
                )}
              </div>
            )}

            <button
              onClick={closeModal}
              className="info-link"
              style={{
                background: "linear-gradient(135deg, #dc2626, #b91c1c)",
                width: "100%",
                padding: "0.8rem",
                border: "none",
                borderRadius: "10px",
              }}
            >
              <span className="link-icon">✕</span>
              Close
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default IndexRatios;
