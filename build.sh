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
import pkg_resources

required = [
    'Flask', 'Flask-Login', 'Flask-SQLAlchemy', 'Flask-Migrate',
    'Flask-WTF', 'Flask-Bcrypt', 'gunicorn', 'psycopg2-binary'
]

installed = [pkg.project_name for pkg in pkg_resources.working_set]
missing = [pkg for pkg in required if pkg not in installed]

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
