#!/bin/bash

# Simple build script for Render deployment
set -e

echo "🚀 Starting ReWear deployment build..."

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install all dependencies
echo "📋 Installing dependencies from requirements.txt..."
pip install --no-cache-dir -r requirements.txt

# Simple verification
echo "🔍 Basic verification..."
python -c "import flask; print('✅ Flask installed successfully')"

echo "🎉 Build process complete!"
