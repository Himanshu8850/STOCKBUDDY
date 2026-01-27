#!/usr/bin/env bash
# Render build script for StockBuddy

set -o errexit  # Exit on error

echo "📦 Installing Node.js dependencies..."
npm install --legacy-peer-deps

echo "🏗️  Building React frontend..."
CI=false npm run build

echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "✅ Build complete! Ready to deploy."
