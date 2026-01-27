// const { set } = require("mongoose");
import API_BASE_URL from './config';

const fetchShares = async (
  setShares,
  setLoading,
  shares,
  setProfitnow,
  setProfit
) => {
  try {
    console.log("fetchshares");

    const response = await fetch(`${API_BASE_URL}/shares`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const sharesData = await response.json();
    let tot = 0.0;
    const shareslist = await Promise.all(
      sharesData.map(async (share) => {
        const profit = await calculateProfit(
          share.symbol,
          share.price,
          share.quantity
        );
        tot += profit[0];
        const prr = [parseInt(profit[0]), parseInt(profit[1])];
        return { ...share, prr };
      })
    );
    const oldprof = await fetch(`${API_BASE_URL}/api/profit`);
    const oldprofval = await oldprof.json();
    setProfitnow(tot);
    localStorage.setItem("prof", JSON.stringify(oldprofval.profit));
    setProfit(oldprofval.profit);
    setShares(shareslist);
    // console.log("hello0", oldprofval);
    // setLoading(true);
    // console.log("fetchshares", shareslist);
    localStorage.setItem("shares", JSON.stringify(shareslist));
    return JSON.stringify(shareslist);
  } catch (error) {
    console.error("Error:", error);
  } finally {
    setLoading(false);
  }
};

const calculateProfit = async (symbol, pri, qtt) => {
  try {
    // console.log("calsymb", symbol);
    const response = await fetch(
      `${API_BASE_URL}/api/searching?symbol=${symbol}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    if (!Array.isArray(data) || typeof data[0] !== "number") {
      return [0, 0];
    }
    const profit = (data[0] - pri) * qtt;
    return [isNaN(profit) ? 0 : parseInt(profit), data[0]];
  } catch (error) {
    return [0, 0]; // Always return a valid array
  }
};

// Function 3
const fetchprof = async (setProfit, setShares, setProfitnow, shares) => {
  let tot = 0;
  console.log("fetchprof");
  const shareslist = await Promise.all(
    shares.map(async (share) => {
      const profit = await calculateProfit(
        share.symbol,
        share.price,
        share.quantity
      );
      const profitVal =
        Array.isArray(profit) && !isNaN(profit[0]) ? profit[0] : 0;
      tot += profitVal;
      return { ...share, profit };
    })
  );
  setProfitnow(tot);
  // console.log(tot);
  setShares(shareslist);
  localStorage.setItem("shares", JSON.stringify(shareslist));

  const oldprof = await fetch(`${API_BASE_URL}/api/profit`);
  const oldprofval = await oldprof.json();
  setProfit(oldprofval.profit); // Update the main profit state
};

// Export all functions
export { fetchShares, calculateProfit, fetchprof };
