#!/usr/bin/env bash
# ================================================================
#  GovShield AI — One-Click Launcher (Linux / macOS)
#  Ayushman Bharat Fraud Detection System v3.3
# ================================================================
set -e

# ── Colors ───────────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'

# ── Banner ────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}  ============================================================${RESET}"
echo -e "${CYAN}${BOLD}     GovShield AI  v3.3 — Ayushman Bharat Fraud Detection${RESET}"
echo -e "${CYAN}${BOLD}  ============================================================${RESET}"
echo ""

# ── Navigate to project root ─────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Step 1: Python check ──────────────────────────────────────────
echo -e "${BOLD}[1/5]${RESET} Checking Python..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo -e "${RED}[ERROR]${RESET} Python not found. Install Python 3.9+ and try again."
    exit 1
fi
PY=$(command -v python3 || command -v python)
echo -e "       Found: $($PY --version)"

# ── Step 2: Virtual environment ───────────────────────────────────
echo -e "${BOLD}[2/5]${RESET} Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "       Creating virtual environment..."
    $PY -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
echo -e "       ${GREEN}venv active${RESET}"

# ── Step 3: Dependencies ──────────────────────────────────────────
echo -e "${BOLD}[3/5]${RESET} Installing / verifying dependencies..."
pip install -r requirements.txt -q 2>&1 | tail -1
echo -e "       ${GREEN}Dependencies ready${RESET}"

# ── Step 4: Sample data ───────────────────────────────────────────
echo -e "${BOLD}[4/5]${RESET} Checking data..."
if [ ! -f "govshield_results.csv" ]; then
    echo "       Generating sample data..."
    $PY main_simple.py >/dev/null 2>&1 || true
    [ -f "govshield_results.csv" ] && echo -e "       ${GREEN}Data generated${RESET}" \
        || echo -e "       ${YELLOW}No data generated — dashboard shows empty state${RESET}"
else
    echo -e "       ${GREEN}Data file found${RESET}"
fi

# ── Step 5: Launch ────────────────────────────────────────────────
echo -e "${BOLD}[5/5]${RESET} Launching GovShield server..."
echo ""
echo -e "${CYAN}${BOLD}  ============================================================${RESET}"
echo -e "    Dashboard : ${BOLD}http://localhost:5000/dashboard${RESET}"
echo -e "    Landing   : ${BOLD}http://localhost:5000/landing${RESET}"
echo -e "    Health    : ${BOLD}http://localhost:5000/api/health${RESET}"
echo ""
echo -e "    ${GREEN}No API keys needed — fully offline capable${RESET}"
echo -e "    ${YELLOW}Press Ctrl+C to stop${RESET}"
echo -e "${CYAN}${BOLD}  ============================================================${RESET}"
echo ""

# Open browser after 3s
(sleep 3 && (
    if command -v xdg-open &>/dev/null; then xdg-open "http://localhost:5000/dashboard"
    elif command -v open &>/dev/null; then open "http://localhost:5000/dashboard"
    fi
)) &

# Start server
$PY flask_app.py

