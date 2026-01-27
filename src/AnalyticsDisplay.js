import React from "react";
import { MoneyIcon, AnalyticsIcon } from "./icons";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

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

  // Prepare data for Pie Chart (Portfolio Distribution)
  const pieChartData = {
    labels: shares.map((share) => share.symbol),
    datasets: [
      {
        data: shares.map((share) => share.price * share.quantity),
        backgroundColor: shares.map((_, i) => {
          const colors = [
            "#00e676",
            "#3385ff",
            "#ff3333",
            "#ffcc00",
            "#8a2be2",
            "#00ffff",
          ]; // Cyberpunk palette
          return colors[i % colors.length];
        }),
        borderColor: "#1a1a2e",
        borderWidth: 1,
      },
    ],
  };

  // Options for Pie Chart
  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: {
          color: "#e0e0e0", // Text primary color for labels
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let label = context.label || "";
            if (label) {
              label += ": ";
            }
            if (context.parsed !== null) {
              label += new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
              }).format(context.parsed);
            }
            return label;
          },
        },
      },
    },
  };

  // Prepare data for Bar Plot (P&L per Stock)
  const barPlotData = {
    labels: shares.map((share) => share.symbol),
    datasets: [
      {
        label: "Profit/Loss",
        data: shares.map((share) =>
          share.profit && share.profit.length > 0 ? share.profit[0] : 0
        ),
        backgroundColor: shares.map(
          (share) =>
            share.profit && share.profit.length > 0 && share.profit[0] >= 0
              ? "#00e676"
              : "#ff3333" // Neon Green for profit, Neon Red for loss
        ),
        borderColor: "#1a1a2e",
        borderWidth: 1,
      },
    ],
  };

  // Options for Bar Plot
  const barPlotOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#e0e0e0",
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let label = context.dataset.label || "";
            if (label) {
              label += ": ";
            }
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
              }).format(context.parsed.y);
            }
            return label;
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: "#a0a0a0", // Secondary text color
          },
          grid: {
            color: "rgba(51, 133, 255, 0.1)", // Subtle blue grid
          },
        },
        y: {
          ticks: {
            color: "#a0a0a0",
            callback: function (value) {
              return new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
              }).format(value);
            },
          },
          grid: {
            color: "rgba(0, 230, 118, 0.1)", // Subtle green grid
          },
        },
      },
    },
  };

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

      <div className="chart-container-wrapper">
        <div className="chart-card">
          <h4 className="chart-title">Portfolio Distribution by Value</h4>
          <div className="chart-content">
            <Pie data={pieChartData} options={pieChartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <h4 className="chart-title">Profit/Loss per Stock</h4>
          <div className="chart-content">
            <Bar data={barPlotData} options={barPlotOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDisplay;
