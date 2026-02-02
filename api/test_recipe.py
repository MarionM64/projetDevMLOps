import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

# Ensure src package is importable
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from src.router.food_router import router as food_router

@pytest.fixture
def app():
    a = FastAPI()
    a.include_router(food_router)
    return a


@pytest.fixture
def client(app):
    return TestClient(app)


def test_recipe_get_id_404error(client, monkeypatch):
    # simulate service returning None (recipe not found)
    def fake_get_recipe_by_id(id_recipe):
        return None

    # Patch the function as referenced by the router to avoid calling the real external API
    monkeypatch.setattr(
        "src.router.food_router.get_recipe_by_id",
        fake_get_recipe_by_id,
    )

    r = client.get("/recipe/-1")
    assert r.status_code == 404
    assert "non trouvée" in r.json()["detail"]


def test_recipe_get_id_success(client, monkeypatch):
    def fake_get_recipe_by_id(id_recipe):
        return {
            "id": id_recipe,
            "title": "Test Recipe"
        }

    def fake_get_like_by_recipe(id_recipe):
        return 5

    # Patch the functions as referenced by the router to avoid calling external services
    monkeypatch.setattr(
        "src.router.food_router.get_recipe_by_id",
        fake_get_recipe_by_id,
    )

    monkeypatch.setattr(
        "src.router.food_router.get_like_by_recipe",
        fake_get_like_by_recipe,
    )

    r = client.get("/recipe/12345")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 12345
    assert data["title"] == "Test Recipe"
    assert data["like"] == 5


def test_recipe_get_id_402error(client, monkeypatch):
    # simulate the external API returning a 402 error by raising HTTPException in the service
    from fastapi import HTTPException

    def fake_get_recipe_by_id(id_recipe):
        raise HTTPException(status_code=402, detail='Your daily points limit of 50 has been reached')

    # Patch the function as referenced by the router to simulate a 402 response
    monkeypatch.setattr(
        "src.router.food_router.get_recipe_by_id",
        fake_get_recipe_by_id,
    )

    r = client.get("/recipe/999")
    assert r.status_code == 402
    assert "points" in r.json()["detail"]
