# StockBuddy Deployment Guide

## Render Deployment Instructions

### Prerequisites
- GitHub account with this repository
- Render account (free tier works)
- MongoDB Atlas database (or other hosted MongoDB)
- Gemini API key

### Step 1: Prepare Environment Variables
You'll need to set these in Render:
- `MONGO_URI`: Your MongoDB connection string
- `GEMINI_API_KEY`: Your Google Gemini API key
- `FRONTEND_URL`: Your Render app URL (e.g., https://stockbuddy.onrender.com)

### Step 2: Deploy on Render

#### Option A: Using render.yaml (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select this repository
5. Render will detect `render.yaml` automatically
6. Add environment variables in the dashboard
7. Click "Apply" to deploy

#### Option B: Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: stockbuddy
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
   - **Environment Variables**: Add MONGO_URI, GEMINI_API_KEY, FRONTEND_URL
5. Click "Create Web Service"

### Step 3: Post-Deployment
1. Wait for build to complete (5-10 minutes first time)
2. Visit your app URL: `https://your-app-name.onrender.com`
3. Test login and demo mode
4. Verify API endpoints are working

### Local Testing Before Deploy
```bash
# Build frontend
npm run build

# Test production build locally
cd backend
gunicorn --bind 0.0.0.0:5000 app:app
```

### Troubleshooting
- **Build fails**: Check that all dependencies in requirements.txt are compatible
- **Static files not loading**: Verify build folder path in app.py
- **API errors**: Check CORS settings and environment variables
- **Slow response**: Render free tier may sleep after inactivity (first request takes 30s)

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month free (enough for one service)

### Upgrading
Consider upgrading Render plan if you need:
- Zero downtime (no sleeping)
- More memory/CPU
- Custom domain
- Multiple services
