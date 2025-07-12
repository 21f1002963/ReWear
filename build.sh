#!/bin/bash

# Build script for Render deployment

echo "Starting ReWear deployment..."

# Upgrade pip to latest version
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify gunicorn installation
echo "Verifying gunicorn installation..."
pip show gunicorn || {
    echo "Gunicorn not found, installing manually..."
    pip install gunicorn==21.2.0
}

echo "Running database migrations..."
# Initialize database if needed
python -c "
import os
from app import app, db
from flask_migrate import upgrade
import sys

print('Initializing Flask app...')
with app.app_context():
    try:
        # Create all tables
        print('Creating database tables...')
        db.create_all()
        print('✅ Database initialized successfully!')
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')
        sys.exit(1)
"

echo "✅ Build completed successfully!"
