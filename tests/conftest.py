"""Test helpers and environment setup for pytest.

Ensure the project root is on sys.path so tests can import project modules
as top-level packages (e.g., `commands`, `drive_manager`). This is a
portable approach that works regardless of how pytest determines its
working directory during collection.
"""
from __future__ import annotations
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Insert at front so tests import local package versions, not installed ones
    sys.path.insert(0, str(ROOT))
