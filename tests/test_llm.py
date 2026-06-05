import pytest
from unittest.mock import MagicMock
from app.llm.client import ask_llm


def test_ask_llm_success(mocker):
    """Тест успешного вызова LLM с возвратом ответа"""

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Привет! Я искусственный интеллект."
    mock_response.choices = [mock_choice]

    mock_groq_client = mocker.patch("app.llm.client.Groq")
    mock_groq_client.return_value.chat.completions.create.return_value = mock_response

    messages = [{"role": "user", "content": "Привет"}]

    response = ask_llm(messages=messages)

    assert response.choices[0].message.content == "Привет! Я искусственный интеллект."


def test_ask_llm_with_tools(mocker):
    """Тест вызова LLM с передачей инструментов (tools)"""

    mock_groq_client = mocker.patch("app.llm.client.Groq")

    test_tools = [{"type": "function", "function": {"name": "get_weather"}}]
    messages = [{"role": "user", "content": "Какая погода?"}]

    # Вызываем функцию, передавая инструменты
    ask_llm(messages=messages, tools=test_tools)

    # Проверяем, что инструменты корректно дошли до API Groq
    mock_groq_client.return_value.chat.completions.create.assert_called_once_with(
        messages=messages,
        model="llama-3.3-70b-versatile",
        tools=test_tools
    )
