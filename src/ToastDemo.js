import React, { useContext } from 'react';
import { MyContext } from './context';

const ToastDemo = () => {
  const { 
    showSuccessToast, 
    showErrorToast, 
    showWarningToast, 
    showInfoToast 
  } = useContext(MyContext);

  const testToasts = () => {
    showSuccessToast("Stock purchased successfully! 🎉");
    setTimeout(() => showErrorToast("Failed to connect to server"), 1000);
    setTimeout(() => showWarningToast("Market volatility detected"), 2000);
    setTimeout(() => showInfoToast("Portfolio updated"), 3000);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h3>Toast Notification Demo</h3>
      <button 
        onClick={testToasts}
        style={{
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        Test Toast Notifications
      </button>
    </div>
  );
};

export default ToastDemo;
