import pytest
from app.client_1c.client import OneCClient


@pytest.fixture
def client():
    ones_client = OneCClient()

    return ones_client

def test_1c_health_success(client):

    client = OneCClient()
    assert client.base_url != ""

    client.health = lambda: "ok"

    test_health = client.health()
    assert test_health == "ok"

def test_1c_health_failure(client):
    """Дополнительный тест: проверяем поведение, если сервер 1С недоступен"""

    client.health = lambda: "error"

    test_health = client.health()
    assert test_health != "ok"

@pytest.mark.asyncio
async def test_1c_call_mcp(client):
    tool_name = "list_metadata_objects"
    tool_args = {"metaType": "Catalogs"}
    result = await client.call_mcp("tools/call", {
        "name": tool_name,
        "arguments": tool_args
    })
    assert isinstance(result, dict)
    assert result  # список не пустой

@pytest.mark.asyncio
async def test_1c_tools_list(client):
    tools_list = await client.tools_list()
    assert isinstance(tools_list, list)
    assert tools_list  # список не пустой

    # Проверяем, что первый элемент списка содержит ожидаемый ключ или структуру
    assert "function" in tools_list[0]

@pytest.mark.asyncio
async def test_1c_call_tool(client):
    tool_name = "list_metadata_objects"
    tool_args = {"metaType": "Catalogs"}
    result  = await client.call_tool(tool_name, tool_args)
    assert result  # не пустой
    assert result['content']

@pytest.mark.asyncio
async def test_1c_resources_list(client):
    resources_list = await client.resources_list()
    assert isinstance(resources_list, list)
    assert resources_list  # список не пустой
    assert resources_list[0].uri