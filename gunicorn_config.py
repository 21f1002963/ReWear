# Gunicorn configuration file for Render deployment

# Server socket
bind = "0.0.0.0:10000"  # Render uses port 10000
backlog = 2048

# Worker processes
workers = 1  # Start with 1 worker, can be increased based on traffic
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 60

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "rewear_app"

# Preload application for better performance
preload_app = True

# Enable automatic worker restarts when code changes
reload = False  # Set to True only for development
