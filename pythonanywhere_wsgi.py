"""WSGI entry point for PythonAnywhere.

In the PythonAnywhere Web tab, set the WSGI file to import `application`
from this module, or copy this file's contents into their generated WSGI file.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("FLASK_ENV", "production")

from app import create_app

application = create_app("production")
