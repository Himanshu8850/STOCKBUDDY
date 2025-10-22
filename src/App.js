import "./App.css";
import "./Toast.css";
import { useEffect, useContext, useState } from "react";
import Search from "./search";
import {
  StockIcon,
  BellIcon,
  RocketIcon,
  RobotIcon,
  AnalyticsIcon,
} from "./icons";
import { MyContext } from "./context";
import Stocks from "./Stocks";
import { fetchShares, fetchprof } from "./functions";
import IndexRatios from "./IndexRatios";
import Alerts from "./Alerts";
// import ChartComponent from "./Chart";
import AnalyticsDisplay from "./AnalyticsDisplay";
import { ToastContainer } from "./Toast";

function App() {
  const {
    port,
    profit,
    setProfit,
    setLoading,
    shares,
    setShares,
    profitnow,
    setProfitnow,
    toasts,
    removeToast,
  } = useContext(MyContext);

  // Navigation state management
  const [currentView, setCurrentView] = useState("dashboard"); // dashboard, tops, alerts, graph, model, analytics
  const [previousView, setPreviousView] = useState("dashboard");
  const [pred, setpred] = useState("");
  const [showSearchBar, setShowSearchBar] = useState(false);
  useEffect(() => {
    const fetchData = async () => {
      const share = localStorage.getItem("shares")
        ? JSON.parse(localStorage.getItem("shares")).map((s) => ({
            ...s,
            price: parseFloat(s.price),
            quantity: parseInt(s.quantity, 10),
          }))
        : []; // Initialize as empty array instead of 'a'

      let sh = localStorage.getItem("prof")
        ? parseFloat(JSON.parse(localStorage.getItem("prof")))
        : 0; // Initialize as 0 instead of 'a'

      if (isNaN(sh)) {
        sh = 0;
      }
      // setProfit(sh); // Removed, profit will be set by fetchShares or fetchprof
      // console.log("sh before storing in localStorage (initial load):", sh);

      if (share.length === 0) {
        const res = await fetchShares(
          setShares,
          setLoading,
          shares,
          setProfitnow,
          setProfit
        );

        const rep = JSON.parse(res);
        setShares(rep);
        localStorage.setItem("shares", JSON.stringify(rep));
        // console.log("profit before storing in localStorage (after fetchShares):", profit);
        // localStorage.setItem("prof", JSON.stringify(profit)); // Redundant, fetchShares already does this
        // setProfit(sh); // This was overwriting the correct profit state
        fetchprof(setProfit, setShares, setProfitnow, rep);
        setLoading(false);
      } else {
        const shar = localStorage.getItem("shares")
          ? JSON.parse(localStorage.getItem("shares")).map((s) => ({
              ...s,
              price: parseFloat(s.price),
              quantity: parseInt(s.quantity, 10),
            }))
          : []; // Initialize as empty array instead of 'a'
        // console.log(
        //   "profit before storing in localStorage (else branch):",
        //   profit
        // );
        // localStorage.setItem("prof", JSON.stringify(profit)); // Redundant if fetchprof handles it
        fetchprof(setProfit, setShares, setProfitnow, shar);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  // Fetch Gemini AI predictions for all stocks in portfolio
  const fetchAIPredictions = async () => {
    if (!shares || shares.length === 0) {
      setpred("No stocks in portfolio to analyze.");
      return;
    }
    setpred("Loading AI predictions...");
    try {
      const symbols = shares.map((s) => s.symbol);
      const res = await fetch("http://localhost:5000/api/ai-predictions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stocks: symbols }),
      });
      const data = await res.json();
      setpred(data);
    } catch (error) {
      setpred("Error fetching AI predictions.");
    }
  };

  const navigateTo = (view) => {
    setPreviousView(currentView);
    setCurrentView(view);
  };

  const goBack = () => {
    setCurrentView(previousView);
    setPreviousView("dashboard");
  };

  const renderHeader = () => (
    <header className="app-header">
      <div className="header-content">
        <h1 className="app-title">
          <StockIcon className="title-icon" />
          STOCKBUDDY
        </h1>

        {/* Navigation Links */}
        <nav className="nav-links">
          <button
            className={`nav-button ${
              currentView === "portfolio" ? "active" : ""
            }`}
            onClick={() => navigateTo("portfolio")}
          >
            Portfolio
          </button>
        </nav>

        {/* Search and Actions */}
        <div className="header-actions">
          <div
            className={`search-container ${showSearchBar ? "expanded" : ""}`}
          >
            <button
              className="search-toggle"
              onClick={() => setShowSearchBar(!showSearchBar)}
              title="Search Stocks"
            >
              🔍
            </button>
            {showSearchBar && (
              <div className="search-wrapper">
                <Search onClose={() => setShowSearchBar(false)} />
              </div>
            )}
          </div>

          {/* Back Button */}
          {currentView !== "dashboard" && (
            <button className="back-button" onClick={goBack}>
              ← Back
            </button>
          )}
        </div>
      </div>
    </header>
  );

  const renderDashboard = () => (
    <div className="dashboard">
      {/* Profit Cards */}
      <div className="profit-cards-container">
        <div className="profit-card present-profit">
          <div className="card-header">
            <span className="card-icon">💰</span>
            <h3>Current P&L</h3>
          </div>
          <div className="card-value">
            <span className={`amount ${profitnow >= 0 ? "profit" : "loss"}`}>
              ₹{Math.abs(profitnow).toLocaleString()}
            </span>
            <span className="label">{profitnow >= 0 ? "Profit" : "Loss"}</span>
          </div>
        </div>

        <div className="profit-card alltime-profit">
          <div className="card-header">
            <span className="card-icon">🏆</span>
            <h3>All Time P&L</h3>
          </div>
          <div className="card-value">
            <span className={`amount ${profit >= 0 ? "profit" : "loss"}`}>
              ₹{Math.abs(profit).toLocaleString()}
            </span>
            <span className="label">{profit >= 0 ? "Profit" : "Loss"}</span>
          </div>
        </div>
      </div>

      {/* Navigation Grid */}
      <div className="nav-grid">
        <div className="nav-card" onClick={() => navigateTo("tops")}>
          <RocketIcon className="nav-icon" />
          <h3>Top Performers</h3>
          <p>Market leaders & trending stocks</p>
        </div>

        <div className="nav-card" onClick={() => navigateTo("alerts")}>
          <BellIcon className="nav-icon" />
          <h3>Market Alerts</h3>
          <p>News, updates & notifications</p>
        </div>

        {/* Charts removed */}

        <div
          className="nav-card"
          onClick={() => {
            fetchAIPredictions();
            navigateTo("model");
          }}
        >
          <RobotIcon className="nav-icon" />
          <h3>AI Predictions</h3>
          <p>AI-powered stock insights</p>
        </div>

        <div className="nav-card" onClick={() => navigateTo("analytics")}>
          <AnalyticsIcon className="nav-icon" />
          <h3>Analytics</h3>
          <p>Portfolio performance metrics</p>
        </div>
      </div>
    </div>
  );

  const renderCurrentView = () => {
    switch (currentView) {
      case "portfolio":
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">📊</span>
              My Portfolio
            </h2>
            <Stocks />
          </div>
        );

      case "tops":
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🚀</span>
              Top Performers
            </h2>
            <IndexRatios />
          </div>
        );

      case "alerts":
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🔔</span>
              Market Alerts
            </h2>
            <Alerts />
          </div>
        );

      // Graph view removed

      case "model":
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🤖</span>
              AI Predictions
            </h2>

            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginBottom: "1.5rem",
              }}
            >
              <button
                className="modern-btn primary"
                onClick={fetchAIPredictions}
              >
                <span className="btn-icon">🔄</span>
                Refresh Predictions
              </button>
            </div>

            {typeof pred === "string" ? (
              pred.toLowerCase().includes("loading") ? (
                <div className="loading-state">
                  <div className="loading-spinner" />
                  <p>Fetching AI insights...</p>
                </div>
              ) : pred.toLowerCase().includes("no stocks") ? (
                <div className="empty-state">
                  <div className="empty-icon">📭</div>
                  <h3>No stocks to analyze</h3>
                  <p>Add stocks to your portfolio to see AI insights.</p>
                </div>
              ) : (
                <div className="error">
                  <span>⚠️</span> {pred}
                </div>
              )
            ) : pred && typeof pred === "object" ? (
              <div className="ai-predictions-grid">
                {Object.entries(pred).map(([symbol, result]) => {
                  const rawVerdict = result?.verdict || "";
                  const verdictText = rawVerdict.toLowerCase();
                  const isError =
                    verdictText.includes("ai error") ||
                    verdictText.includes("error");
                  const category = verdictText.includes("swing buy")
                    ? "Swing Buy"
                    : verdictText.includes("avoid")
                    ? "Avoid"
                    : verdictText.includes("neutral")
                    ? "Neutral"
                    : rawVerdict || "Uncertain";
                  const reason = rawVerdict
                    .replace(/^(swing buy|avoid|neutral)[:\.\s-]*/i, "")
                    .trim();
                  let verdictClass = "neutral";
                  if (category.toLowerCase() === "swing buy")
                    verdictClass = "positive";
                  else if (category.toLowerCase() === "avoid")
                    verdictClass = "negative";
                  return (
                    <div key={symbol} className="ai-prediction-card">
                      <div className="ai-card-header">
                        <div className="ai-symbol">
                          <span className="ai-symbol-icon">🏷️</span>
                          {symbol}
                        </div>
                        <div
                          className={`verdict-badge ${verdictClass}`}
                          title={rawVerdict}
                        >
                          {category}
                        </div>
                      </div>

                      {reason && !isError && (
                        <div className="verdict-reason">{reason}</div>
                      )}

                      {isError ? (
                        <div className="ai-card-error">
                          Service unavailable. Please refresh in a moment.
                        </div>
                      ) : (
                        <div className="ai-card-content">
                          <div className="ai-section">
                            <div className="ai-section-title pros">Pros</div>
                            <ul className="ai-list pros-list">
                              {(result?.pros || []).length > 0 ? (
                                result.pros.map((p, i) => (
                                  <li key={i}>
                                    <span className="bullet pros">✅</span>
                                    <span className="text">{p}</span>
                                  </li>
                                ))
                              ) : (
                                <li className="muted">No pros provided</li>
                              )}
                            </ul>
                          </div>

                          <div className="ai-section">
                            <div className="ai-section-title cons">Cons</div>
                            <ul className="ai-list cons-list">
                              {(result?.cons || []).length > 0 ? (
                                result.cons.map((c, i) => (
                                  <li key={i}>
                                    <span className="bullet cons">❌</span>
                                    <span className="text">{c}</span>
                                  </li>
                                ))
                              ) : (
                                <li className="muted">No cons provided</li>
                              )}
                            </ul>
                          </div>
                        </div>
                      )}

                      <div className="ai-card-footer">
                        <span className="ai-powered">✨ Powered by Gemini</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
        );

      case "analytics":
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">📈</span>
              Portfolio Analytics
            </h2>
            <AnalyticsDisplay shares={shares} />
          </div>
        );

      default:
        return renderDashboard();
    }
  };

  return (
    <div className="app">
      {renderHeader()}
      <main className="app-main">{renderCurrentView()}</main>
      {/* Toast Container for notifications */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}

export default App;
