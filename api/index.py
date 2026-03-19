"""Vercel serverless function entry point."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# Vercel expects a handler named 'app' or 'handler'
handler = app
