import React, { createContext, useState } from "react";

export const MyContext = createContext();

export const MyContextProvider = ({ children }) => {
  const [data, setData] = useState(null);
  const [text, setText] = useState("");
  const [qty, setQty] = useState(0);
  const [shares, setShares] = useState(null);
  const [load, setLoading] = useState(false);
  const [al, setal] = useState(false);
  const [port, setport] = useState(false);
  const [profit, setProfit] = useState(0);
  const [profitnow, setProfitnow] = useState(0);
  const [chartData, setChartData] = useState(null);
  const [chart, setChart] = useState(null);
  const [update, setupdate] = useState(false);
  
  // Toast notification state
  const [toasts, setToasts] = useState([]);

  // Toast functions
  const addToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now() + Math.random();
    const newToast = { id, message, type, duration };
    setToasts(prev => [...prev, newToast]);
    return id;
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const showSuccessToast = (message, duration = 3000) => {
    return addToast(message, 'success', duration);
  };

  const showErrorToast = (message, duration = 4000) => {
    return addToast(message, 'error', duration);
  };

  const showWarningToast = (message, duration = 3500) => {
    return addToast(message, 'warning', duration);
  };

  const showInfoToast = (message, duration = 3000) => {
    return addToast(message, 'info', duration);
  };

  return (
    <MyContext.Provider
      value={{
        data,
        setData,
        chartData,
        chart,
        setChart,
        setChartData,
        text,
        setText,
        load,
        shares,
        qty,
        setQty,
        port,
        profit,
        profitnow,
        setProfitnow,
        setProfit,
        update,
        setupdate,
        setport,
        setShares,
        setLoading,
        al,
        setal,
        // Toast functions
        toasts,
        addToast,
        removeToast,
        showSuccessToast,
        showErrorToast,
        showWarningToast,
        showInfoToast,
      }}
    >
      {children}
    </MyContext.Provider>
  );
};
