import json

from app.llm.client import ask_llm
from app.client_1c.client import OneCClient

OneCClient = OneCClient()

async def run_agent(message: str):

    tools_list = await OneCClient.tools_list()
    messages = [
        {
            "role": "system",
            "content": """ 
                Ты помощник 1С.
                
                Алгоритм работы:
                1. Если нужны данные из базы:
                1.1 Получение списка отчетов "list_reports".
                1.2. Найди подходящий по описанию.
                1.3. Если не находишь подходящий, другие инструменты не вызываешь.
                1.4. Если найден подходящий - для выполнения вызываешь run_report.
                1.5. Результат выполнения возвращается в виде таблицы.
                
                2. Если нужны данные о структуре базы:
                2.1 Сначала вызови list_metadata_objects
                2.2 Используй только объекты из результата list_metadata_objects
                3.2 Описание объекта только из результата get_metadata_structure
                3.4 Если вернулась ошибка - не продолжай
                
                3. Никогда не придумывай метаданные
                4. Если вернулась ошибка - не продолжай
            """
        },
        {
            "role": "user",
            "content": message,
        }
    ]

    while True:

        completions = ask_llm(messages, tools_list)
        choice = completions.choices[0]

        if choice.finish_reason != "tool_calls":
            answer = {
                "content": choice.message.content,
                "messages": messages
            }
            return answer

        messages.append(choice.message)

        for tool_call in choice.message.tool_calls:
            args = json.loads(tool_call.function.arguments)

            result = await OneCClient.call_tool(
                tool_call.function.name,
                args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })


