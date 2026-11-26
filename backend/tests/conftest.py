"""Pytest configuration and fixtures for SafeTriage."""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path so 'app' can be imported cleanly
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.triage.nlp_extractor import NLPExtractor


@pytest.fixture
def extractor() -> NLPExtractor:
    return NLPExtractor()
