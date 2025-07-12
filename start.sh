#!/bin/bash

# Start command for Render
echo "Starting ReWear application..."

# Check if gunicorn is available
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found, installing..."
    pip install gunicorn==21.2.0
fi

# Start the application
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
