import pytest
import httpx
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))
    


@pytest.fixture
def client(app):
    return TestClient(app)

