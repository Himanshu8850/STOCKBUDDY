import { useContext, useEffect, useState, React } from "react"; // Added React import if not globally available
import { MyContext } from "./context";
import { fetchShares } from "./functions";

const Stocks = () => {
  const {
    load,
    shares,
    setShares,
    update,
    setupdate,
    showSuccessToast,
    showErrorToast,
  } = useContext(MyContext);
  const [disabled, setDisabled] = useState(false);

  const sell = async (symbol, profit) => {
    setDisabled(true);
    try {
      const res = await fetch(
        `http://localhost:5000/api/sell?symbol=${symbol}&profit=${profit}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (res.ok) {
        const updatedShares = () => {
          setupdate(true);
          const filteredShares = Array.isArray(shares)
            ? shares.filter((share) => share.symbol !== symbol)
            : [];

          localStorage.setItem("shares", JSON.stringify(filteredShares));
          setShares(filteredShares);
          setDisabled(false);
          setupdate(false);
        };
        updatedShares();

        // Calculate and show profit/loss
        const profitText =
          profit >= 0
            ? `Sold ${symbol} with a profit of ₹${Math.abs(
                profit
              ).toLocaleString()}!`
            : `Sold ${symbol} with a loss of ₹${Math.abs(
                profit
              ).toLocaleString()}`;

        showSuccessToast(profitText);
      } else {
        showErrorToast(`Failed to sell ${symbol}. Please try again.`);
        setDisabled(false);
      }
    } catch (error) {
      console.error("Error selling share:", error);
      showErrorToast(`Error selling ${symbol}: ${error.message}`);
      setDisabled(false);
    }
  };

  return (
    <div className="stocks-container">
      {/* Content Section */}
      <div className="stocks-content">
        {load && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your portfolio...</p>
          </div>
        )}

        {!update && shares !== null && !load && (
          <>
            {!shares || shares.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📈</div>
                <h3>No Shares in Portfolio</h3>
                <p>Start investing by searching and buying your first stock!</p>
              </div>
            ) : (
              <div className="stocks-grid">
                {shares.map((share, index) => {
                  // Add safety checks for profit data
                  const profitData = share.profit || [0, share.price || 0];
                  const profitAmount = profitData[0] || 0;
                  const currentPrice = profitData[1] || share.price || 0;
                  const buyPrice = share.price || 0;
                  const changePercent =
                    buyPrice > 0
                      ? ((currentPrice - buyPrice) / buyPrice) * 100
                      : 0;

                  return (
                    <div className="performance-card" key={index}>
                      <div className="card-header">
                        <div className="rank-badge">
                          {share.symbol || "Unknown"}
                        </div>
                        <div
                          className={`change-indicator ${
                            profitAmount >= 0 ? "positive" : "negative"
                          }`}
                        >
                          {profitAmount >= 0 ? "+" : "-"}
                        </div>
                      </div>

                      <div className="card-content">
                        <h3 className="stock-name">
                          {share.symbol || "Unknown Stock"}
                        </h3>

                        <div className="price-section">
                          <div className="current-price">
                            <span className="price-label">Current Price</span>
                            <span className="price-value">
                              ₹{currentPrice.toFixed(2)}
                            </span>
                          </div>

                          <div className="price-change">
                            <span
                              className={`change-value ${
                                changePercent >= 0 ? "positive" : "negative"
                              }`}
                            >
                              {changePercent >= 0 ? "+" : ""}
                              {changePercent.toFixed(2)}%
                            </span>
                            <span className="change-amount">
                              ₹{(currentPrice - buyPrice).toFixed(2)}
                            </span>
                          </div>
                        </div>

                        <div className="stock-details">
                          <div className="detail-item">
                            <span className="detail-label">Bought At</span>
                            <span className="detail-value">
                              ₹{buyPrice.toFixed(2)}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="detail-label">Quantity</span>
                            <span className="detail-value">
                              {share.quantity || 0}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="detail-label">Total P&L</span>
                            <span
                              className={`detail-value ${
                                profitAmount >= 0 ? "positive" : "negative"
                              }`}
                            >
                              {profitAmount >= 0 ? "+" : ""}₹
                              {Math.abs(profitAmount).toLocaleString()}
                            </span>
                          </div>
                        </div>

                        <div className="card-actions">
                          <button
                            className={`info-link ${
                              disabled ? "disabled" : ""
                            }`}
                            onClick={() =>
                              sell(share.symbol, parseInt(profitAmount))
                            }
                            disabled={disabled}
                            style={{
                              background: disabled
                                ? "#94a3b8"
                                : "linear-gradient(135deg, #dc2626, #b91c1c)",
                              cursor: disabled ? "not-allowed" : "pointer",
                              width: "100%",
                            }}
                          >
                            <span className="link-icon">
                              {disabled ? "…" : "Sell"}
                            </span>
                            {disabled ? "Selling..." : "Sell Stock"}
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Stocks;
