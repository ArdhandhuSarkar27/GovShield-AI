"""
UI Utilities
============
Utility functions for the Streamlit web app to suppress terminal output
and provide clean UI interactions.
"""

import sys
import os
from contextlib import contextmanager
from io import StringIO

@contextmanager
def suppress_stdout():
    """
    Context manager to suppress stdout (print statements) when running
    fraud detection in the UI to keep terminal clean.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

@contextmanager
def capture_stdout():
    """
    Context manager to capture stdout and return it as a string.
    Useful for debugging or showing process output in UI.
    """
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        yield captured_output
    finally:
        sys.stdout = old_stdout

def format_currency(amount):
    """Format amount as Indian currency"""
    return f"₹{amount:,.0f}"

def get_status_color(status):
    """Get color for fraud status"""
    colors = {
        'FLAGGED': '#f44336',
        'REVIEW': '#ff9800',
        'CLEAR': '#4caf50'
    }
    return colors.get(status, '#007bff')

def get_status_icon(status):
    """Get icon for fraud status"""
    icons = {
        'FLAGGED': '🚨',
        'REVIEW': '⚠️',
        'CLEAR': '✅'
    }
    return icons.get(status, 'ℹ️')