#!/usr/bin/env bash
# GovShield Quick-Start Script
set -e
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛡️  GovShield v3.2 — Quick Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Load .env if present
[ -f .env ] && export $(grep -v '^#' .env | xargs)

# 2. Install dependencies if venv not present
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt -q

# 3. Generate data if CSV missing
if [ ! -f "govshield_results.csv" ]; then
  echo "Generating sample data..."
  python main_simple.py 2>/dev/null || true
fi

# 4. Start server
echo ""
echo "Starting server..."
echo "  Dashboard: http://localhost:5000/dashboard"
echo "  Landing:   http://localhost:5000/landing"
echo ""

if command -v gunicorn &>/dev/null; then
  gunicorn wsgi:application -c gunicorn.conf.py
else
  python flask_app.py
fi
