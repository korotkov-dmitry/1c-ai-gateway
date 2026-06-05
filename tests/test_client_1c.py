import json
import pytest
import respx
from httpx import Response
from app.client_1c.client import OneCClient
from mcp import types


@pytest.fixture
def client():
    """Фикстура для создания инстанса OneCClient.
    Поскольку settings подгружает URL, base_url будет взят из конфига."""
    return OneCClient()


# ==========================================
# 1. ТЕСТ МЕТОДА health()
# ==========================================

@pytest.mark.asyncio
@respx.mock  # Декоратор активирует перехватчик httpx запросов
async def test_health_success(client):
    # Настраиваем перехват GET запроса на эндпоинт health
    # client.base_url подставится автоматически
    respx.get(f"{client.base_url}/mcp/health").mock(
        return_value=Response(200, json={"status": "ok"})
    )

    status = await client.health()

    assert status == "ok"


# ==========================================
# 2. ТЕСТ ОБРАБОТКИ ОШИБОК JSON-RPC
# ==========================================

@pytest.mark.asyncio
@respx.mock
async def test_call_mcp_json_rpc_error(client):
    # Имитируем ответ от 1С, содержащий ошибку JSON-RPC спецификации
    mock_error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }

    respx.post(f"{client.base_url}/mcp").mock(
        return_value=Response(200, json=mock_error_response)
    )

    # Проверяем, что метод call_mcp корректно парсит ошибку и выбрасывает Exception
    with pytest.raises(Exception) as exc_info:
        await client.call_mcp("unknown/method")

    assert "JSON-RPC ошибка -32601: Method not found" in str(exc_info.value)


# ==========================================
# 3. ТЕСТ МЕТОДА tools_list()
# ==========================================

@pytest.mark.asyncio
@respx.mock
async def test_tools_list(client):
    mock_rpc_result = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {"name": "read_db", "description": "Чтение базы"},
                {"name": "write_db", "description": "Запись в базу"}
            ]
        }
    }

    # Перехватываем POST-запрос
    route = respx.post(f"{client.base_url}/mcp").mock(
        return_value=Response(200, json=mock_rpc_result)
    )

    tools = await client.tools_list()

    # Проверяем, что ушел валидный JSON-RPC пакет
    assert route.called
    request_bytes = route.calls.last.request.content
    request_json = json.loads(request_bytes)
    assert request_json["method"] == "tools/list"
    assert request_json["jsonrpc"] == "2.0"

    # Проверяем итоговый результат
    assert isinstance(tools, list)
    assert len(tools) == 2
    assert tools[0]["name"] == "read_db"


# ==========================================
# 4. ТЕСТ МЕТОДА resources_list() (Конвертация в типы MCP)
# ==========================================

@pytest.mark.asyncio
@respx.mock
async def test_resources_list_mapping(client):
    mock_rpc_result = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "resources": [
                {
                    "uri": "file://resource/",
                    "name": "Товары",
                    "description": "Справочник номенклатуры",
                    "mimeType": "application/json"
                }
            ]
        }
    }

    respx.post(f"{client.base_url}/mcp").mock(
        return_value=Response(200, json=mock_rpc_result)
    )

    resources = await client.resources_list()

    assert isinstance(resources, list)
    assert len(resources) == 1

    # Самая важная проверка: убеждаемся, что сырой dict превратился в объект класса types.Resource
    resource_object = resources[0]
    assert isinstance(resource_object, types.Resource)
    assert str(resource_object.uri) == "file://resource/"
    assert resource_object.name == "Товары"
    assert resource_object.description == "Справочник номенклатуры"
    assert resource_object.mimeType == "application/json"
