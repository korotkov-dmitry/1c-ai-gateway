from groq import Groq
from app.config import settings

def ask_llm(messages: list, tools=None):
    client = Groq(
        api_key=settings.groq_api_key,
    )

    model = "llama-3.1-8b-instant"
    #model_v = "llama-3.3-70b-versatile"  # основная

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        tools=tools,
        tool_choice="auto",
    )

    return response