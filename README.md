# 📈 STOCKBUDDY

<div align="center">

![STOCKBUDDY](https://img.shields.io/badge/STOCKBUDDY-Paper%20Trading%20Platform-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=flat-square&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=flat-square&logo=mongodb)
![AI](https://img.shields.io/badge/AI-Gemini%202.0-FF6F00?style=flat-square&logo=google)

**A sophisticated paper trading platform with AI-powered stock analysis**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 📊 Paper Trading
- **Virtual Trading Environment**: Practice stock trading with zero financial risk
- **Real-time NSE Stock Data**: Live price updates from Indian stock market via Groww API
- **Portfolio Management**: Buy and sell stocks with automatic profit/loss tracking
- **Transaction History**: Track all-time and current P&L across your portfolio

### 🤖 AI-Powered Analysis
- **Gemini AI Integration**: Advanced stock analysis powered by Google's Gemini 2.5 Pro
- **Swing Trading Insights**: Get AI-generated pros, cons, and trading verdicts for portfolio stocks
- **Automated Predictions**: Batch processing for analyzing multiple stocks simultaneously
- **Smart Recommendations**: Actionable insights categorized as "Swing Buy", "Neutral", or "Avoid"

### 📈 Analytics & Monitoring
- **Portfolio Analytics**: Comprehensive metrics including total value, P&L, holdings count
- **Performance Tracking**: Real-time profit/loss calculations for individual stocks
- **Market Alerts**: Stay updated with relevant market news and notifications
- **Top Performers**: View market leaders and trending stocks

### 💻 Modern UI/UX
- **Responsive Design**: Beautiful interface built with React and TailwindCSS
- **Real-time Updates**: Auto-refresh portfolio data every 15 seconds
- **Toast Notifications**: User-friendly success/error messages
- **Intuitive Navigation**: Clean dashboard with easy access to all features

---

## 🛠 Tech Stack

### Frontend
- **React 18.3** - Modern UI library
- **TailwindCSS** - Utility-first styling
- **Chart.js & Recharts** - Data visualization
- **Socket.io Client** - Real-time communication
- **React Modal** - Enhanced user interactions

### Backend
- **Flask 2.3** - Lightweight Python web framework
- **MongoDB & MongoEngine** - NoSQL database for portfolio persistence
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP library for external API calls

### AI & Data Processing
- **Google Gemini 2.5 Pro** - Advanced language model for stock analysis
- **NumPy & Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning utilities
- **TensorFlow & Keras** - Deep learning framework

### APIs & Integration
- **Groww API** - Real-time Indian stock market data (NSE)
- **Google Gemini API** - AI-powered stock predictions

---

## 🚀 Getting Started

### Prerequisites

```bash
# Required software
- Python 3.8+
- Node.js 14+
- MongoDB (local or cloud instance)
- Git
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/STOCKBUDDY.git
cd STOCKBUDDY
```

2. **Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure Environment Variables**

Create a `.env` file in the `backend/` directory:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/stockbuddy

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  # Alternative key name
GEMINI_MODEL=gemini-2.5-pro

# Flask Configuration
PORT=5000
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=stockbuddy.log
```

4. **Frontend Setup**
```bash
# Return to root directory
cd ..

# Install dependencies
npm install
```

5. **Database Setup**
```bash
# Start MongoDB (if running locally)
mongod --dbpath /path/to/your/db

# MongoDB will automatically create the required collections on first run
```

### Running the Application

**Option 1: Run both servers simultaneously**
```bash
npm start
```
This command uses `concurrently` to start both the Flask backend and React frontend.

**Option 2: Run servers separately**

Terminal 1 (Backend):
```bash
cd backend
python3 app.py
```

Terminal 2 (Frontend):
```bash
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

---

## 📖 Usage

### 1. **Search for Stocks**
- Click the search icon (🔍) in the header
- Enter stock symbol (e.g., "TCS", "INFY", "RELIANCE")
- View real-time price and stock details

### 2. **Buy Stocks**
- Search for a stock
- Enter desired quantity
- Click "Buy" to add to your portfolio
- Transaction is recorded with current market price

### 3. **View Portfolio**
- Navigate to "Portfolio" tab
- See all your holdings with:
  - Current price and P&L
  - Buy price and quantity
  - Percentage change
  - Total profit/loss

### 4. **Sell Stocks**
- Click "Sell" on any stock card
- Profit/loss is automatically calculated
- Transaction is recorded in all-time P&L

### 5. **AI Analysis**
- Navigate to "AI Predictions"
- Click "Refresh Predictions" for latest insights
- View AI-generated pros, cons, and trading verdict for each stock
- Get swing trading recommendations (1-4 week horizon)

### 6. **Analytics Dashboard**
- View total portfolio value
- Track total and average P&L
- Monitor number of holdings
- Analyze performance metrics

---

## 🔌 API Documentation

### Stock Endpoints

#### Search Stock
```http
GET /api/searching?symbol={SYMBOL}
```
Returns current price and market data for a stock.

#### Buy Stock
```http
POST /buy
Content-Type: application/json

{
  "symbol": "TCS",
  "price": 3450.50,
  "qtx": 10
}
```

#### Sell Stock
```http
DELETE /api/sell?symbol={SYMBOL}&profit={PROFIT}
```

#### Get Portfolio
```http
GET /shares
```
Returns all stocks in the user's portfolio.

#### Get Profit/Loss
```http
GET /api/profit
```
Returns total all-time profit/loss.

### AI Endpoints

#### Get AI Predictions
```http
POST /api/ai-predictions
Content-Type: application/json

{
  "stocks": ["TCS", "INFY", "RELIANCE"]
}
```

**Response:**
```json
{
  "TCS": {
    "pros": ["Strong momentum", "Good volume"],
    "cons": ["Overhead resistance", "Market volatility"],
    "verdict": "Swing Buy - Bullish momentum with good risk/reward"
  },
  "INFY": { ... }
}
```

### Health Check
```http
GET /health
```
Returns server health status and database connectivity.

---

## 📊 Database Schema

### Share Collection
```javascript
{
  symbol: String,      // NSE scrip code
  price: Float,        // Average buy price
  quantity: Integer,   // Number of shares
  created_at: Float    // Unix timestamp
}
```

### Profit Collection
```javascript
{
  symbol: String,      // NSE scrip code
  profit: Float,       // Total profit/loss
  last_updated: Float  // Unix timestamp
}
```

---

## 🎨 Color Theme

The application uses a sophisticated color palette for optimal UX:
- **Primary**: Light Green - Success and positive indicators
- **Danger**: Red - Loss and negative indicators  
- **Info**: Blue - Neutral information and highlights
- **Background**: Clean white with subtle gradients

---

## 🔐 Security Features

- **Input Validation**: All user inputs are sanitized and validated
- **API Timeout Protection**: External API calls have configurable timeouts
- **Error Handling**: Comprehensive error catching and logging
- **CORS Configuration**: Restricted to authorized origins only
- **Environment Variables**: Sensitive data stored in `.env` file

---

## 📝 Configuration

### Frontend Configuration (`package.json`)
- Modify `start` script to change backend startup behavior
- Adjust `proxy` settings for API endpoint routing

### Backend Configuration (`config.py`)
- Development, Testing, and Production environments
- Configurable logging levels
- Database connection pooling settings

---

## 🧪 Development

### Running Tests
```bash
# Frontend tests
npm test

# Backend tests (if implemented)
cd backend
pytest
```

### Building for Production
```bash
# Create optimized production build
npm run build

# Build output will be in /build directory
```

---

## 🚧 Roadmap

- [ ] Add historical data charts and technical indicators
- [ ] Implement user authentication and multi-user support
- [ ] Add watchlist functionality
- [ ] Support for options and futures trading
- [ ] Mobile app (React Native)
- [ ] Advanced portfolio analytics with ML insights
- [ ] Integration with more exchanges (BSE, international markets)
- [ ] Social features (share portfolios, follow traders)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- **Groww**: For providing reliable Indian stock market data API
- **Google Gemini**: For powering the AI analysis features
- **Create React App**: For the excellent React boilerplate
- **MongoDB**: For flexible NoSQL database solution
- **Open Source Community**: For the amazing libraries and tools

---

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on [GitHub Issues](https://github.com/yourusername/STOCKBUDDY/issues)
- Email: your.email@example.com

---

## ⚠️ Disclaimer

**STOCKBUDDY is a paper trading platform for educational and practice purposes only.**

- This application uses simulated trading and does not involve real money
- Stock predictions are AI-generated and should not be considered financial advice
- Always consult with a qualified financial advisor before making investment decisions
- Past performance does not guarantee future results
- The developers are not responsible for any financial decisions made based on this application

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

Made with ❤️ and ☕ for traders and developers

</div>
