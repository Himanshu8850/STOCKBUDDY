import "./App.css";
import { useEffect, useContext, useState } from "react";
import Search from "./search";
import { MyContext } from "./context";
import Stocks from "./Stocks";
import { fetchShares, fetchprof } from "./functions";
import IndexRatios from "./IndexRatios";
import Alerts from "./Alerts";
import ChartComponent from "./Chart";
import AnalyticsDisplay from "./AnalyticsDispay";
function App() {
  const {
    port,
    profit,
    setProfit,
    setLoading,
    shares,
    setShares,
    load, // Note: 'load' is declared but not used in the provided snippet
    profitnow,
    setProfitnow,
  } = useContext(MyContext);

  const [tops, settops] = useState(false);
  const [alerts, setalerts] = useState(false);
  const [graph, setgraphs] = useState(false);
  const [model, setmodel] = useState(false);
  const [pred, setpred] = useState("");
  const [analytics, setAnalytics] = useState(true);
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
  }, [setLoading]);

  const fetchmod = async () => {
    const modout = await fetch("http://localhost:5000/api/model");

    const modres = await modout.json();

    setpred("hello");
  };

  // Define new colors for profit/loss backgrounds that fit the dark theme
  // These are derived from the UI's existing palette or complementary tones
  const profitBackgroundColor = "#28A745"; // A good green (You can fine-tune this)
  const lossBackgroundColor = "#DC3545"; // A good red (You can fine-tune this)

  // Use the card background color from your CSS for consistency
  // Note: To directly access CSS variables here, you might need a different approach
  // or define these as JS constants if they're purely for JS-driven styles.
  // For now, I'll use a fixed color close to --card-background defined in your CSS.
  const cardDefaultBackgroundColor = "#25254A"; // Approx value of var(--card-background)

  return (
    <div
      className="App"
      // Change App background based on profit, using new dark-theme friendly colors
      style={{
        backgroundColor: "#25254A",
      }}
    >
      {!port && <Search />}
      {!port && (
        <div className="profit-cards">
          <h2
            className="present-card"
            style={{
              // Change card background based on profitnow, using new colors
              color:
                profitnow > 0
                  ? profitBackgroundColor // Darker green for present profit
                  : lossBackgroundColor, // Darker red for present loss
              // Or keep it consistent with the overall card background if profit/loss is shown inside
              // backgroundColor: cardDefaultBackgroundColor,
            }}
          >
            Present
            <hr style={{ margin: "0" }} />
            {profitnow > 0 ? `Profit: ₹${profitnow}` : `Loss: ₹${profitnow}`}
          </h2>

          <h2
            className="alltime-card"
            style={{
              // Change card background based on overall profit, using new colors
              color:
                profit > 0
                  ? profitBackgroundColor // Darker green for all-time profit
                  : lossBackgroundColor, // Darker red for all-time loss
              // Or keep it consistent with the overall card background
              // backgroundColor: cardDefaultBackgroundColor,
            }}
          >
            AllTime
            <hr style={{ margin: "0" }} />
            {profit > 0 ? `Profit: ₹${profit}` : `Loss: ₹${profit}`}
          </h2>
        </div>
      )}
      {port && <Stocks />}

      <button
        className="button-52 hb"
        onClick={() => {
          setalerts(false);
          settops((prev) => !prev);
        }}
      >
        TOPS!
      </button>
      <button
        className="button-52 hb"
        onClick={() => {
          settops(false);
          setalerts((prev) => !prev);
        }}
      >
        Alerts!
      </button>
      <button
        className="button-52 hb"
        onClick={() => {
          setgraphs((prev) => !prev);
        }}
      >
        Graph
      </button>
      <button
        className="button-52 hb"
        onClick={() => {
          fetchmod();
          setmodel((prev) => !prev);
        }}
      >
        model
      </button>

      <div className="misc-container">
        {graph && (
          <div className="chartdiv">
            <ChartComponent />
          </div>
        )}
        {pred && <h2>{pred}</h2>}
        {tops && <IndexRatios />}
        {alerts && <Alerts />}
        {analytics && <AnalyticsDisplay shares={shares} />}
      </div>
    </div>
  );
}

export default App;
