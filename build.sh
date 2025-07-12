#!/bin/bash

# Build script for Render deployment
set -e

echo "🚀 Starting ReWear deployment build..."

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install all dependencies
echo "📋 Installing dependencies from requirements.txt..."
pip install --no-cache-dir -r requirements.txt

# Verify installations
echo "🔍 Verifying installations..."
python -c "
import sys

required = [
    'flask', 'flask_login', 'flask_sqlalchemy', 'flask_migrate',
    'flask_wtf', 'flask_bcrypt', 'gunicorn', 'psycopg2'
]

print('Checking required packages...')
missing = []
for pkg in required:
    try:
        __import__(pkg)
        print(f'✅ {pkg} - OK')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg} - MISSING')

if missing:
    print(f'❌ Missing packages: {missing}')
    sys.exit(1)
else:
    print('✅ All required packages installed successfully')
"

# Initialize database
echo "🗄️  Initializing database..."
python -c "
import os
import sys

print('Loading Flask app...')
try:
    from app import app, db
    
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        print('✅ Database initialized successfully!')
        
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    # Don't exit here, let the app handle database creation at runtime
    print('⚠️  Will attempt database creation at runtime')

print('✅ Build completed successfully!')
"

echo "🎉 Build process complete!"
