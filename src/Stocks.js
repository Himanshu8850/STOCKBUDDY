import { useContext, useEffect, useState, React } from "react"; // Added React import if not globally available
import { MyContext } from "./context";
import { fetchShares } from "./functions";

const Stocks = () => {
  const { load, shares, setport, setShares, update, setupdate } =
    useContext(MyContext);
  const [disabled, setDisabled] = useState(false);

  // Define colors that align with the new dark theme
  // These should match the CSS variables you defined or be close approximations
  const BG_DARK_BLUE = "#1A1A32";
  const ACCENT_VIBRANT_BLUE = "#4A6BF7";
  const ACCENT_ELECTRIC_PINK = "#F72C6A";
  const TEXT_WHITE = "#FFFFFF";
  const CARD_BACKGROUND = "#25254A";
  const PROFIT_BACKGROUND = "#28A745"; // Darker green for profit state
  const LOSS_BACKGROUND = "#DC3545"; // Darker red for loss state

  const sell = async (symbol, profit) => {
    // Changed 'index' to 'symbol' for clarity, assuming index is the symbol
    setDisabled(true);
    const res = await fetch(
      `http://localhost:5000/api/sell?symbol=${symbol}&profit=${profit}`,
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const updatedShares = () => {
      setupdate(true);
      // Ensure 'shares' is an array before filtering
      const filteredShares = Array.isArray(shares)
        ? shares.filter((share) => share.symbol !== symbol)
        : [];

      localStorage.setItem("shares", JSON.stringify(filteredShares));
      setShares(filteredShares); // Pass the filtered array directly
      // fetchShares(); // This might cause an infinite loop or unexpected behavior if not carefully managed
      // If fetchShares updates shares state, it might conflict with immediate setShares.
      // Consider if you really need to refetch ALL shares immediately after a single sell.
      setDisabled(false);
      setupdate(false);
    };
    updatedShares();
    // console.log(res.json()); // This would log a Promise, not the resolved JSON.
  };

  const portchange = () => {
    setport(false);
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          backgroundColor: CARD_BACKGROUND, // Changed to a color from the new theme
          width: "100vw",
          position: "relative",
          zIndex: "0",
        }}
      >
        <h2
          style={{
            backgroundColor: CARD_BACKGROUND, // Changed to a color from the new theme
            fontSize: "35px",
            width: "300px",
            marginTop: 20,
            color: TEXT_WHITE, // Changed text color to white
          }}
        >
          MY SHARES
        </h2>
        <button
          className="button-52 hb" // `hb` class already has the blue background from CSS
          onClick={portchange}
          style={{ margin: "10px 0 0 0" }} // Keep specific margins
        >
          Search
        </button>
      </div>
      <div className="login-box">
        {load && <h1>Loading..</h1>} {/* Using 'load' state */}
        {!update && shares !== null && (
          <>
            {!shares || shares.length === 0 ? ( // Check for empty array too
              <h1>No Shares</h1>
            ) : (
              <div className="shares-container">
                {shares.map((share, index) => (
                  <div
                    className="share"
                    key={index}
                    style={{
                      backgroundColor: "#25254A",
                    }}
                  >
                    <h1
                      style={{
                        color: "lightcyan", // Changed text color to white
                        backgroundColor:
                          share.profit[0] > 0
                            ? PROFIT_BACKGROUND // Use new profit color
                            : LOSS_BACKGROUND, // Use new loss color
                        fontSize: "25px",
                      }}
                    >
                      {share.symbol}
                    </h1>
                    <div style={{ height: "50px" }}>
                      {" "}
                      {/* Consider removing fixed height if content varies */}
                      <div>
                        <span>
                          Change :{" "}
                          {(
                            ((share.profit[1] - share.price) / share.price) *
                            100
                          ).toFixed(2)}
                          %
                        </span>
                        <span>Bought at: {share.price.toFixed(2)}</span>
                        <span>Curr: {share.profit[1]}</span>
                      </div>
                      <div>
                        <span>Qty: {share.quantity}</span>
                        <span>Profit: {share.profit[0]}</span>
                      </div>
                    </div>
                    <button
                      className="button-52 hll" // `hll` class already has the pink background from CSS
                      onClick={() =>
                        sell(share.symbol, parseInt(share.profit[0]))
                      }
                      style={{
                        // 'disabled' is a boolean prop, not a style property
                        // Instead of disabled: disabled, use the 'disabled' prop directly on the button
                        position: "relative",
                        top: "100px",
                        margin: "70px 0px 0px 0px",
                      }}
                      disabled={disabled} // Correct way to disable the button
                    >
                      Sell
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Stocks;
