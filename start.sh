#!/bin/bash

# Start command for Render
echo "Starting ReWear application..."

# Ensure we're using the virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Using virtual environment: $VIRTUAL_ENV"
else
    echo "No virtual environment detected, using system Python"
fi

# Verify critical dependencies
echo "Verifying dependencies..."
python -c "
import sys
try:
    import flask
    import flask_migrate
    import gunicorn
    print('✅ All critical dependencies found')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload app:app
