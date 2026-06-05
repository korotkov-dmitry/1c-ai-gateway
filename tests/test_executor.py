import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.agent.executor import run_agent

@pytest.mark.asyncio
async def test_run_agent_with_tool_call_loop(mocker):
    """Тест проверяет полный цикл работы агента: вызов инструмента и финальный ответ"""

    # --- 1. МОКАЕМ ONE C CLIENT ---
    # Перехватываем глобальный объект OneCClient, созданный внутри файла агента
    mock_1c = mocker.patch("app.agent.executor.OneCClient")

    # Настраиваем возвращаемые значения для асинхронных методов 1С
    mock_1c.tools_list = AsyncMock(return_value=[{"type": "function", "name": "list_metadata_objects"}])
    mock_1c.call_tool = AsyncMock(return_value={"status": "success", "data": ["Справочник.Номенклатура"]})

    # --- 2. МОКАЕМ LLM (ДВА ОТВЕТА ДЛЯ ЦИКЛА WHILE) ---
    mock_ask_llm = mocker.patch("app.agent.executor.ask_llm")

    # Шаг 1: Ответ от LLM с требованием вызвать инструмент
    mock_choice_1 = MagicMock()
    mock_choice_1.finish_reason = "tool_calls"

    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_abc123"
    mock_tool_call.function.name = "list_metadata_objects"
    mock_tool_call.function.arguments = '{"filter": "all"}'

    mock_choice_1.message.tool_calls = [mock_tool_call]
    # Нам нужно сохранить сам объект сообщения, так как агент делает messages.append(choice.message)
    mock_message_1 = MagicMock()
    mock_message_1.tool_calls = [mock_tool_call]
    mock_choice_1.message = mock_message_1

    # Шаг 2: Финальный ответ от LLM после получения данных из инструмента
    mock_choice_2 = MagicMock()
    mock_choice_2.finish_reason = "stop"
    mock_choice_2.message.content = "Я нашел метаданные: Справочник.Номенклатура."

    # Объединяем ответы: при первом вызове ask_llm вернет шаг 1, при втором — шаг 2
    mock_completions_1 = MagicMock()
    mock_completions_1.choices = [mock_choice_1]

    mock_completions_2 = MagicMock()
    mock_completions_2.choices = [mock_choice_2]

    # side_effect позволяет выдавать разные ответы при последовательных вызовах
    mock_ask_llm.side_effect = [mock_completions_1, mock_completions_2]

    # --- 3. ЗАПУСК ТЕСТИРУЕМОЙ ФУНКЦИИ ---
    user_message = "Покажи справочники из 1С"
    final_answer = await run_agent(user_message)

    # --- 4. ПРОВЕРКИ (ASSERTIONS) ---

    # Проверяем, что агент вернул правильный финальный ответ ИИ
    assert final_answer == "Я нашел метаданные: Справочник.Номенклатура."

    # Проверяем, что список инструментов запрашивался у клиента 1С
    mock_1c.tools_list.assert_called_once()

    # Проверяем, что ask_llm вызвался ровно 2 раза (сначала за инструментом, потом за ответом)
    assert mock_ask_llm.call_count == 2

    # Проверяем, что инструмент 1С был вызван с правильным именем и распарсенными аргументами
    mock_1c.call_tool.assert_called_once_with(
        "list_metadata_objects",
        {"filter": "all"}
    )
