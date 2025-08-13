// const { set } = require("mongoose");

const fetchShares = async (
  setShares,
  setLoading,
  shares,
  setProfitnow,
  setProfit
) => {
  try {
    console.log("fetchshares");

    const response = await fetch("http://localhost:5000/shares", {
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
    const oldprof = await fetch("http://localhost:5000/api/profit");
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
      `http://localhost:5000/api/searching?symbol=${symbol}`,
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
    // console.log(data);
    // console.log("calcprof", shares);
    return [parseInt((data[0] - pri) * qtt), data[0]];
  } catch (error) {
    // console.error(`Error calculating profit for ${symbol}:`, error);
    return 0; // Default to 0 profit if error occurs
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
      tot += profit[0];
      return { ...share, profit };
    })
  );
  setProfitnow(tot);
  // console.log(tot);
  setShares(shareslist);
  localStorage.setItem("shares", JSON.stringify(shareslist));
  // console.log("fetchprof", shares);
  // setProfit(res.json().profit);
};

// Export all functions
export {
  fetchShares,
  calculateProfit,
  fetchprof,
};
