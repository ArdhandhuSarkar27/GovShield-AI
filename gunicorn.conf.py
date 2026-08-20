"""Gunicorn configuration for GovShield production deployment."""
import multiprocessing, os

workers          = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class     = 'sync'
timeout          = 120
keepalive        = 5
bind             = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
accesslog        = 'logs/access.log'
errorlog         = 'logs/error.log'
loglevel         = 'info'
preload_app      = True
max_requests     = 1000
max_requests_jitter = 50
worker_tmp_dir   = '/dev/shm'
