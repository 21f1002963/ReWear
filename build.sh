#!/bin/bash

# Build script for Render deployment

echo "Starting ReWear deployment..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
# Initialize database if needed
python -c "
from app import app, db
from flask_migrate import upgrade
import os

with app.app_context():
    if not os.path.exists('migrations'):
        from flask_migrate import init
        init()
    
    # Create all tables
    db.create_all()
    print('Database initialized successfully!')
"

echo "Build completed successfully!"
