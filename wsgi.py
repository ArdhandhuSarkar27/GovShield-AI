"""
wsgi.py — WSGI entry point for GovShield.
Use with: gunicorn wsgi:application
or: gunicorn -c gunicorn.conf.py wsgi:application
"""
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask_app import app as application

if __name__ == '__main__':
    application.run()
