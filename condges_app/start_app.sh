#!/bin/bash

# CONDGES Dashboard Startup Script
echo "🚀 Starting CONDGES Dashboard..."

# Navigate to app directory
cd "$(dirname "$0")"

# Activate virtual environment
source ~/.virtualenvs/hotelops_condges/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    echo "💡 Make sure hotelops_condges virtual environment exists"
    exit 1
fi

# Set port
export PORT=5001

# Start the Flask app
echo "🌐 Starting Flask app on port $PORT..."
python app.py
