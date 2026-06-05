import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

def test_health_endpoint(test_client):
    """Тест проверяет, что эндпоинт /health возвращает статус 200 и нужный JSON"""

    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

