# Gunicorn configuration file for Render deployment
import os

# Server socket - Render provides PORT environment variable
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"

# Worker processes - Keep it simple for free tier
workers = 1
worker_class = "sync"
timeout = 120  # Increased timeout for slow operations
keepalive = 60

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "rewear_app"

# Preload application for better performance
preload_app = True
