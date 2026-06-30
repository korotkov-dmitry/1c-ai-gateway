import json

from app.llm.client import ask_llm
from app.client_1c.client import OneCClient

OneCClient = OneCClient()

async def run_agent(message: str,
                    system_role: str,
                    model: str=None,
                    message_content: str=None):

    tools_list = await OneCClient.tools_list()
    messages = [
        {
            "role": "system",
            "content": system_role
        }
    ]

    messages.extend(message_content)

    messages.append({
        "role": "user",
        "content": message,
    })

    while True:

        completions = ask_llm(messages,
                              model,
                              tools_list)
        choice = completions.choices[0]

        if choice.finish_reason != "tool_calls":
            answer = {
                "content": choice.message.content,
                "messages": messages,
                "id": completions.id
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


