import "./App.css";
import "./Toast.css";
import { useEffect, useContext, useState } from "react";
import Search from "./search";
import { MyContext } from "./context";
import Stocks from "./Stocks";
import { fetchShares, fetchprof } from "./functions";
import IndexRatios from "./IndexRatios";
import Alerts from "./Alerts";
import ChartComponent from "./Chart";
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
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, tops, alerts, graph, model, analytics
  const [previousView, setPreviousView] = useState('dashboard');
  const [pred, setpred] = useState("");
  const [showSearchBar, setShowSearchBar] = useState(false);
  useEffect(() => {
    const fetchData = async () => {
      const share = localStorage.getItem("shares")
        ? JSON.parse(localStorage.getItem("shares"))
        : "a";

      const sh = localStorage.getItem("prof")
        ? JSON.parse(localStorage.getItem("prof"))
        : "a";

      setProfit(sh);

      if (share === "a" || sh === "a") {
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
        localStorage.setItem("prof", JSON.stringify(sh));
        setProfit(sh);
        fetchprof(setProfit, setShares, setProfitnow, rep);
        setLoading(false);
      } else {
        const shar = JSON.parse(localStorage.getItem("shares"));
        fetchprof(setProfit, setShares, setProfitnow, shar);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, [setLoading, setProfit, setProfitnow, setShares, shares]);

  const fetchmod = async () => {
    try {
      const modout = await fetch("http://localhost:5000/api/model");
      const modres = await modout.json();
      console.log("Model response:", modres);
      setpred("AI Prediction Model Loaded Successfully!");
    } catch (error) {
      console.error("Error loading model:", error);
      setpred("Error loading AI model. Please ensure backend is running.");
    }
  };

  const navigateTo = (view) => {
    setPreviousView(currentView);
    setCurrentView(view);
  };

  const goBack = () => {
    setCurrentView(previousView);
    setPreviousView('dashboard');
  };

  const renderHeader = () => (
    <header className="app-header">
      <div className="header-content">
        <h1 className="app-title">
          <span className="title-icon">📈</span>
          STOCKBUDDY
        </h1>
        
        {/* Navigation Links */}
        <nav className="nav-links">
          <button 
            className={`nav-button ${currentView === 'portfolio' ? 'active' : ''}`}
            onClick={() => navigateTo('portfolio')}
          >
            Portfolio
          </button>
        </nav>

        {/* Search and Actions */}
        <div className="header-actions">
          <div className={`search-container ${showSearchBar ? 'expanded' : ''}`}>
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
          {currentView !== 'dashboard' && (
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
            <span className={`amount ${profitnow >= 0 ? 'profit' : 'loss'}`}>
              ₹{Math.abs(profitnow).toLocaleString()}
            </span>
            <span className="label">{profitnow >= 0 ? 'Profit' : 'Loss'}</span>
          </div>
        </div>

        <div className="profit-card alltime-profit">
          <div className="card-header">
            <span className="card-icon">🏆</span>
            <h3>All Time P&L</h3>
          </div>
          <div className="card-value">
            <span className={`amount ${profit >= 0 ? 'profit' : 'loss'}`}>
              ₹{Math.abs(profit).toLocaleString()}
            </span>
            <span className="label">{profit >= 0 ? 'Profit' : 'Loss'}</span>
          </div>
        </div>
      </div>

      {/* Navigation Grid */}
      <div className="nav-grid">
        <div className="nav-card" onClick={() => navigateTo('tops')}>
          <div className="nav-icon">🚀</div>
          <h3>Top Performers</h3>
          <p>Market leaders & trending stocks</p>
        </div>

        <div className="nav-card" onClick={() => navigateTo('alerts')}>
          <div className="nav-icon">🔔</div>
          <h3>Market Alerts</h3>
          <p>News, updates & notifications</p>
        </div>

        <div className="nav-card" onClick={() => navigateTo('graph')}>
          <div className="nav-icon">📊</div>
          <h3>Charts</h3>
          <p>Technical analysis & trends</p>
        </div>

        <div className="nav-card" onClick={() => {
          fetchmod();
          navigateTo('model');
        }}>
          <div className="nav-icon">🤖</div>
          <h3>AI Predictions</h3>
          <p>Machine learning insights</p>
        </div>

        <div className="nav-card" onClick={() => navigateTo('analytics')}>
          <div className="nav-icon">📈</div>
          <h3>Analytics</h3>
          <p>Portfolio performance metrics</p>
        </div>
      </div>
    </div>
  );

  const renderCurrentView = () => {
    switch(currentView) {
      case 'portfolio':
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">📊</span>
              My Portfolio
            </h2>
            <Stocks />
          </div>
        );
        
      case 'tops':
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🚀</span>
              Top Performers
            </h2>
            <IndexRatios />
          </div>
        );
      
      case 'alerts':
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🔔</span>
              Market Alerts
            </h2>
            <Alerts />
          </div>
        );
      
      case 'graph':
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">📊</span>
              Charts & Analysis
            </h2>
            <ChartComponent />
          </div>
        );
      
      case 'model':
        return (
          <div className="view-container">
            <h2 className="view-title">
              <span className="title-icon">🤖</span>
              AI Predictions
            </h2>
            {pred && <div className="prediction-result">{pred}</div>}
            <div className="model-placeholder">
              <p>Advanced ML models are analyzing market trends...</p>
            </div>
          </div>
        );
      
      case 'analytics':
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
      <main className="app-main">
        {renderCurrentView()}
      </main>
      {/* Toast Container for notifications */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}

export default App;
