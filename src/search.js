import { useContext } from "react";
import React from "react";
import { MyContext } from "./context";
import API_BASE_URL from './config';
import { SearchIcon, MoneyIcon } from "./icons";
import { fetchShares } from "./functions";
const Search = ({ onClose }) => {
  const {
    data,
    setData,
    text,
    setShares,
    setQty,
    setLoading,
    load,
    setProfitnow,
    setProfit,
    setal,
    shares,
    setupdate,
    setText,
    al,
    qty,
    showSuccessToast,
    showErrorToast,
    showWarningToast,
  } = useContext(MyContext);
  const getch = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/searching?symbol=${text}`
      );
      if (response.ok) {
        const data = await response.json();
        if (data[0] == null) {
          showErrorToast("Please enter a valid stock symbol");
          setLoading(false);
          return;
        }
        setData(data);
        showSuccessToast(`Found ${data[1][2]} - ₹${data[0].toFixed(2)}`);
        setLoading(false);
      } else {
        showErrorToast("Please enter a valid stock symbol");
      }
    } catch (err) {
      showErrorToast(`Error fetching stock data: ${err.message}`);
      setLoading(false);
    }
  };
  const qtychange = (e) => {
    setal(false);
    setQty(e.target.value);
  };
  const inputadd = (e) => {
    setText(e.target.value);
    setData(null);
  };
  const buyclick = async () => {
    if (!qty) {
      setal(true);
      showWarningToast("Please specify quantity before buying");
    } else {
      try {
        const response = await fetch(`${API_BASE_URL}/buy`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ symbol: text, price: data[0], qtx: qty }),
        });

        if (response.ok) {
          setupdate(true);
          await fetchShares(
            setShares,
            setLoading,
            shares,
            setProfitnow,
            setProfit
          );
          setupdate(false);

          showSuccessToast(
            `Successfully purchased ${qty} shares of ${
              data[1][2]
            } at ₹${data[0].toFixed(2)} each!`
          );
          setData(null);
          setText("");
          setQty("");

          // Close the search component after successful purchase
          if (onClose) {
            onClose();
          }
        } else {
          showErrorToast("Failed to purchase stock. Please try again.");
        }
      } catch (err) {
        showErrorToast(`Purchase failed: ${err.message}`);
      }
    }
  };
  return (
    <div className="modern-search-container">
      <div className="search-header">
        <div className="search-title">
          <span className="search-icon">
            <SearchIcon />
          </span>
          <h2>Stock Search</h2>
        </div>
        {onClose && (
          <button
            className="close-button"
            onClick={onClose}
            title="Close Search"
          >
            ✕
          </button>
        )}
      </div>

      <div className="search-form">
        <div className="modern-input-group">
          <input
            type="text"
            value={text}
            onChange={inputadd}
            placeholder="Enter Stock Symbol"
            className="modern-input"
          />
          <button
            className="modern-btn primary"
            onClick={getch}
            disabled={!text || load}
          >
            {load ? (
              <div className="ai-loader">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
                <span className="label">Thinking…</span>
              </div>
            ) : (
              <>
                <span className="btn-icon">
                  <SearchIcon />
                </span>
                Fetch
              </>
            )}
          </button>
        </div>

        {data && (
          <div className="stock-details">
            <div className="stock-info-card">
              <div className="stock-header">
                <h3 className="stock-name">{data[1][2]}</h3>
                <div className="stock-price">
                  <span className="current-price">₹{data[0].toFixed(2)}</span>
                  <span
                    className={`price-change ${
                      data[0] - data[1][0] >= 0 ? "positive" : "negative"
                    }`}
                  >
                    {data[0] - data[1][0] >= 0 ? "+" : ""}
                    {(data[0] - data[1][0]).toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="stock-stats">
                <div className="stat-item">
                  <span className="stat-label">Open</span>
                  <span className="stat-value">₹{data[1][0].toFixed(2)}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Current</span>
                  <span className="stat-value">₹{data[0].toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="quantity-section">
              <div className="modern-input-group">
                <input
                  type="number"
                  onChange={qtychange}
                  placeholder="Enter Quantity"
                  className="modern-input"
                  min="1"
                  value={qty}
                />
                <button
                  className="modern-btn success"
                  onClick={buyclick}
                  disabled={!qty}
                >
                  <span className="btn-icon">
                    <MoneyIcon />
                  </span>
                  Buy Stock
                </button>
              </div>

              {al && (
                <div className="error-message">
                  <span className="error-icon">⚠️</span>
                  Please specify quantity!
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;
