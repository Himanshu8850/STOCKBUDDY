#!/usr/bin/env bash
# Render build script for StockBuddy

set -o errexit  # Exit on error

echo "📦 Installing Node.js dependencies..."
npm install --legacy-peer-deps

echo "🏗️  Building React frontend..."
CI=false npm run build

echo "🐍 Installing Python dependencies (Python: $(python --version))..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

echo "✅ Build complete! Ready to deploy."
