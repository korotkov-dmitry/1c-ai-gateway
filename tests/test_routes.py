import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.api.routes import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client

def test_chat_endpoint_success(client, mocker):
    """Тест проверяет успешную обработку POST запроса и возврат JSON"""

    mock_run_agent = mocker.patch("app.api.routes.run_agent", new_callable=AsyncMock)
    mock_run_agent.return_value = "Ответ от ИИ-агента 1С"

    payload = {"message": "Покажи остатки товаров"}

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json() == {"result": "Ответ от ИИ-агента 1С"}

    mock_run_agent.assert_called_once_with("Покажи остатки товаров")

def test_chat_endpoint_validation_error(client, mocker):
    """Тест проверяет, что при неверном формате данных API возвращает ошибку 422"""

    mock_run_agent = mocker.patch("app.api.routes.run_agent", new_callable=AsyncMock)
    bad_payload = {"text": "Привет"}

    response = client.post("/chat", json=bad_payload)

    assert response.status_code == 422
    mock_run_agent.assert_not_called()
